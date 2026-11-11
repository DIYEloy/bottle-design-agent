"""Tiered model routing: an expensive planner, cheap workers, free code.

The point of this module is cost. Running every step of the pipeline on a
frontier model is wasteful, because most steps do not need one. Each specialist
is assigned a tier, and only the tier that genuinely needs reasoning gets the
expensive model.

    BRAIN   one call per job. Interprets the brief and commits to a
            composition. This is the only step where model quality visibly
            changes the output.

    WORKER  cheap, high-volume, structured. Copy fitting, validation
            summaries, asset tagging. A small model is sufficient because the
            output shape is constrained and the judgement is shallow.

    LOCAL   no model at all. Geometry, rendering, screening, export,
            measurement. Deterministic code, zero marginal cost.

The single largest cost saving is not choosing a cheaper model: it is noticing
how much of this pipeline is LOCAL. Rendering, halftoning and export were never
model work.

Credentials are read from the environment only, never from arguments or disk:

    BOTTLE_PROVIDER      anthropic | openai | mock   (default: mock)
    BOTTLE_BRAIN_MODEL   model id for the planning tier
    BOTTLE_WORKER_MODEL  model id for the worker tier
    ANTHROPIC_API_KEY / OPENAI_API_KEY

With no provider configured this falls back to the offline mock backend, so
the pipeline stays runnable with no credentials.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from enum import Enum
from typing import Any, Protocol


class Tier(str, Enum):
    BRAIN = "brain"
    WORKER = "worker"
    LOCAL = "local"


#: Which tier each specialist runs on.
#:
#: ``layout`` is BRAIN because composition is the decision that determines
#: whether the artwork is any good. ``theme_planner`` is BRAIN because it sets
#: the creative direction the layout depends on. Everything else is either
#: shallow structured work or not model work at all.
AGENT_TIERS: dict[str, Tier] = {
    "theme_planner": Tier.BRAIN,
    "layout": Tier.BRAIN,
    "image_analysis": Tier.WORKER,
    "asset_placement": Tier.WORKER,
    "quality_review": Tier.WORKER,
}


@dataclass(frozen=True)
class TierConfig:
    provider: str
    brain_model: str | None
    worker_model: str | None
    max_tokens: int = 4096

    @classmethod
    def from_env(cls) -> "TierConfig":
        return cls(
            provider=os.environ.get("BOTTLE_PROVIDER", "mock").strip().lower(),
            brain_model=os.environ.get("BOTTLE_BRAIN_MODEL") or None,
            worker_model=os.environ.get("BOTTLE_WORKER_MODEL") or None,
            max_tokens=int(os.environ.get("BOTTLE_MAX_TOKENS", "4096")),
        )

    def model_for(self, tier: Tier) -> str | None:
        return self.brain_model if tier is Tier.BRAIN else self.worker_model


class _Caller(Protocol):
    async def __call__(self, *, model: str, system: str, user: str,
                       max_tokens: int) -> str: ...


# ---------------------------------------------------------------- providers
async def _call_anthropic(*, model: str, system: str, user: str,
                          max_tokens: int) -> str:
    try:
        from anthropic import AsyncAnthropic
    except ImportError as exc:  # pragma: no cover - depends on optional extra
        raise RuntimeError(
            "provider 'anthropic' requires the anthropic package: "
            "pip install -e '.[providers]'"
        ) from exc
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise RuntimeError("ANTHROPIC_API_KEY is not set")
    client = AsyncAnthropic()
    resp = await client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return "".join(getattr(b, "text", "") for b in resp.content)


async def _call_openai(*, model: str, system: str, user: str,
                       max_tokens: int) -> str:
    try:
        from openai import AsyncOpenAI
    except ImportError as exc:  # pragma: no cover - depends on optional extra
        raise RuntimeError(
            "provider 'openai' requires the openai package: "
            "pip install -e '.[providers]'"
        ) from exc
    if not os.environ.get("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is not set")
    client = AsyncOpenAI()
    resp = await client.chat.completions.create(
        model=model,
        max_tokens=max_tokens,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    return resp.choices[0].message.content or ""


PROVIDERS: dict[str, _Caller] = {
    "anthropic": _call_anthropic,
    "openai": _call_openai,
}


# ------------------------------------------------------------------ parsing
def parse_json_object(raw: str) -> dict[str, Any]:
    """Pull one JSON object out of a model response.

    Tolerates fenced code blocks and leading prose, both of which small models
    emit regularly even when told not to.
    """
    text = raw.strip()
    if text.startswith("```"):
        text = text.split("```")[1] if "```" in text[3:] else text[3:]
        if text.lstrip().lower().startswith("json"):
            text = text.lstrip()[4:]
    text = text.strip()
    try:
        value = json.loads(text)
    except json.JSONDecodeError:
        start, end = text.find("{"), text.rfind("}")
        if start == -1 or end <= start:
            raise ValueError(f"no JSON object in response: {raw[:200]!r}")
        value = json.loads(text[start:end + 1])
    if not isinstance(value, dict):
        raise ValueError("expected a JSON object at the top level")
    return value


# ------------------------------------------------------------------ backend
class TieredBackend:
    """An ``AgentBackend`` that routes each specialist to its tier's model.

    Satisfies the protocol in ``agents.runtime``; drop it in wherever
    ``MockBackend`` is used.
    """

    def __init__(self, config: TierConfig | None = None,
                 tiers: dict[str, Tier] | None = None):
        self.config = config or TierConfig.from_env()
        self.tiers = dict(tiers or AGENT_TIERS)
        self.call_log: list[dict[str, Any]] = []
        self._mock = None
        if self.config.provider == "mock" or self.config.provider not in PROVIDERS:
            from agents.mock_backend import MockBackend
            self._mock = MockBackend()

    def tier_for(self, agent_name: str) -> Tier:
        return self.tiers.get(agent_name, Tier.WORKER)

    def describe(self) -> dict[str, Any]:
        """Report the active routing. Useful in job reports and in the API."""
        return {
            "provider": self.config.provider,
            "using_mock": self._mock is not None,
            "brain_model": self.config.brain_model,
            "worker_model": self.config.worker_model,
            "routing": {a: t.value for a, t in self.tiers.items()},
        }

    async def complete_json(self, *, system_prompt: str,
                            input_data: dict[str, Any],
                            agent_name: str) -> dict[str, Any]:
        tier = self.tier_for(agent_name)
        if self._mock is not None:
            self.call_log.append({"agent": agent_name, "tier": tier.value,
                                  "model": None, "mocked": True})
            return await self._mock.complete_json(
                system_prompt=system_prompt, input_data=input_data,
                agent_name=agent_name)

        model = self.config.model_for(tier)
        if not model:
            env = "BOTTLE_BRAIN_MODEL" if tier is Tier.BRAIN else "BOTTLE_WORKER_MODEL"
            raise RuntimeError(f"{env} is not set but {agent_name!r} needs tier {tier.value}")

        caller = PROVIDERS[self.config.provider]
        user = (
            "Respond with one JSON object and nothing else.\n\n"
            + json.dumps(input_data, indent=2, default=str)
        )
        raw = await caller(model=model, system=system_prompt, user=user,
                           max_tokens=self.config.max_tokens)
        self.call_log.append({"agent": agent_name, "tier": tier.value,
                              "model": model, "mocked": False})
        return parse_json_object(raw)


def build_backend() -> TieredBackend:
    """Construct the backend from the environment."""
    return TieredBackend()
