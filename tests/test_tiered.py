"""Tier routing, env handling, and tolerant JSON parsing."""
from __future__ import annotations

import asyncio

import pytest

from agents.tiered import (AGENT_TIERS, Tier, TierConfig, TieredBackend,
                           parse_json_object)


def test_planning_agents_are_brain_rest_are_worker():
    assert AGENT_TIERS["theme_planner"] is Tier.BRAIN
    assert AGENT_TIERS["layout"] is Tier.BRAIN
    assert AGENT_TIERS["image_analysis"] is Tier.WORKER
    assert AGENT_TIERS["asset_placement"] is Tier.WORKER
    assert AGENT_TIERS["quality_review"] is Tier.WORKER


def test_only_two_agents_use_the_expensive_tier():
    brains = [a for a, t in AGENT_TIERS.items() if t is Tier.BRAIN]
    assert len(brains) == 2, f"expensive tier grew: {brains}"


def test_unknown_agent_defaults_to_worker():
    assert TieredBackend().tier_for("something_new") is Tier.WORKER


def test_defaults_to_mock_without_a_provider(monkeypatch):
    monkeypatch.delenv("BOTTLE_PROVIDER", raising=False)
    backend = TieredBackend()
    assert backend.describe()["using_mock"] is True


def test_unknown_provider_falls_back_to_mock(monkeypatch):
    monkeypatch.setenv("BOTTLE_PROVIDER", "not-a-provider")
    assert TieredBackend().describe()["using_mock"] is True


def test_config_reads_models_from_env(monkeypatch):
    monkeypatch.setenv("BOTTLE_PROVIDER", "anthropic")
    monkeypatch.setenv("BOTTLE_BRAIN_MODEL", "big-model")
    monkeypatch.setenv("BOTTLE_WORKER_MODEL", "small-model")
    cfg = TierConfig.from_env()
    assert cfg.model_for(Tier.BRAIN) == "big-model"
    assert cfg.model_for(Tier.WORKER) == "small-model"


def test_missing_model_for_tier_is_an_explicit_error(monkeypatch):
    monkeypatch.setenv("BOTTLE_PROVIDER", "anthropic")
    monkeypatch.delenv("BOTTLE_BRAIN_MODEL", raising=False)
    monkeypatch.setenv("BOTTLE_WORKER_MODEL", "small-model")
    backend = TieredBackend()
    with pytest.raises(RuntimeError, match="BOTTLE_BRAIN_MODEL"):
        asyncio.run(backend.complete_json(
            system_prompt="x", input_data={}, agent_name="layout"))


def test_mock_backend_still_satisfies_the_pipeline(monkeypatch):
    monkeypatch.setenv("BOTTLE_PROVIDER", "mock")
    backend = TieredBackend()
    out = asyncio.run(backend.complete_json(
        system_prompt="x", input_data={"job": {"theme": "t"}, "profile": {}},
        agent_name="theme_planner"))
    assert "concept" in out
    assert backend.call_log[0]["tier"] == "brain"
    assert backend.call_log[0]["mocked"] is True


@pytest.mark.parametrize("raw", [
    '{"a": 1}',
    '```json\n{"a": 1}\n```',
    '```\n{"a": 1}\n```',
    'Here you go:\n{"a": 1}',
    '  \n {"a": 1}  ',
])
def test_json_parsing_tolerates_common_model_noise(raw):
    assert parse_json_object(raw) == {"a": 1}


@pytest.mark.parametrize("raw", ["no json here", "[1,2,3]", ""])
def test_json_parsing_rejects_non_objects(raw):
    with pytest.raises(ValueError):
        parse_json_object(raw)
