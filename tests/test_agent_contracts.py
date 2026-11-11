from agents.contracts import DesignJob
from agents.runtime import build_agent_definitions


def test_agent_registry_has_expected_specialists():
    names = {definition.name for definition in build_agent_definitions()}
    assert names == {
        "image_analysis",
        "theme_planner",
        "asset_placement",
        "layout",
        "quality_review",
    }


def test_job_defaults_to_monochrome_1200_dpi():
    job = DesignJob(theme="Dental clinic", profile_id="fat_500ml")
    assert job.black_and_white_only is True
    assert job.dpi == 1200
    assert job.reference_assets == []
