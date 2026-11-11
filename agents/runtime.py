"""Runtime for specialist agents backed by any structured-output LLM provider."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

PROMPT_DIR = Path(__file__).resolve().parent / "prompts"


class AgentBackend(Protocol):
    """Adapter contract. Implement this with the chosen model provider."""

    async def complete_json(
        self, *, system_prompt: str, input_data: dict[str, Any], agent_name: str
    ) -> dict[str, Any]:
        """Return one JSON object; raise on provider or parse errors."""
        ...


@dataclass(frozen=True)
class AgentDefinition:
    name: str
    prompt_file: str
    output_key: str
    required_fields: tuple[str, ...] = ()


class SpecialistAgent:
    def __init__(self, definition: AgentDefinition, backend: AgentBackend):
        self.definition = definition
        self.backend = backend

    def system_prompt(self) -> str:
        path = PROMPT_DIR / self.definition.prompt_file
        return path.read_text(encoding="utf-8")

    async def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        result = await self.backend.complete_json(
            system_prompt=self.system_prompt(),
            input_data=input_data,
            agent_name=self.definition.name,
        )
        if not isinstance(result, dict):
            raise TypeError(f"{self.definition.name} must return a JSON object")
        missing = [key for key in self.definition.required_fields if key not in result]
        if missing:
            raise ValueError(f"{self.definition.name} omitted required fields: {missing}")
        # Enforce JSON-serializability at the agent boundary.
        json.dumps(result)
        return result


def build_agent_definitions() -> list[AgentDefinition]:
    return [
        AgentDefinition("image_analysis", "image_analysis.md", "image_analysis", ("assets",)),
        AgentDefinition("theme_planner", "theme_planner.md", "creative_brief", ("concept", "visual_hierarchy")),
        AgentDefinition("asset_placement", "asset_placement.md", "asset_plan", ("placements", "missing_assets")),
        AgentDefinition("layout", "layout.md", "layout_spec", ("canvas", "elements")),
        AgentDefinition("quality_review", "quality_review.md", "quality_report", ("passed", "issues", "warnings")),
    ]


def build_agents(backend: AgentBackend) -> dict[str, SpecialistAgent]:
    return {
        definition.name: SpecialistAgent(definition, backend)
        for definition in build_agent_definitions()
    }
