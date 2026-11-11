import asyncio

import pytest

from agents.contracts import DesignJob
from agents.orchestrator import DesignOrchestrator


class FakeBackend:
    async def complete_json(self, *, system_prompt, input_data, agent_name):
        responses = {
            "image_analysis": {"assets": [], "overall_notes": "No references supplied."},
            "theme_planner": {
                "concept": "Minimal geometric dental theme",
                "visual_hierarchy": ["hero graphic"],
                "composition": {},
                "style_rules": {},
                "avoid": [],
                "open_questions": [],
            },
            "asset_placement": {"placements": [], "missing_assets": []},
            "layout": {
                "canvas": {"width_px": 9000, "height_px": 6000, "dpi": 1200},
                "elements": [],
            },
            "quality_review": {
                "passed": True,
                "issues": [],
                "warnings": ["Printer seam settings remain unverified."],
                "checks": {},
                "recommendations": [],
            },
        }
        return responses[agent_name]


def test_prepare_runs_specialists_in_order():
    orchestrator = DesignOrchestrator(FakeBackend())
    state = asyncio.run(orchestrator.prepare(DesignJob("Dental", "fat_500ml")))
    assert state.blocked is False
    assert [entry["agent"] for entry in state.history] == [
        "image_analysis",
        "theme_planner",
        "asset_placement",
        "layout",
        "quality_review",
    ]


def test_final_export_requires_explicit_approval():
    orchestrator = DesignOrchestrator(FakeBackend(), final_exporter=lambda layout, profile: {})
    state = asyncio.run(orchestrator.prepare(DesignJob("Dental", "fat_500ml")))
    with pytest.raises(PermissionError):
        orchestrator.export_final(state, user_approved=False)


def test_unsupported_color_policy_is_rejected():
    orchestrator = DesignOrchestrator(FakeBackend())
    job = DesignJob("Dental", "fat_500ml", black_and_white_only=False)
    with pytest.raises(ValueError):
        asyncio.run(orchestrator.prepare(job))
