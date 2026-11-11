import asyncio

from agents.mock_backend import MockBackend


def test_mock_backend_returns_layout_for_profile():
    result = asyncio.run(MockBackend().complete_json(
        system_prompt="", agent_name="layout",
        input_data={"job": {"theme": "Ocean", "required_text": ["hello"]},
                    "profile": {"width_px": 9000, "height_px": 6000}}
    ))
    assert result["canvas"]["width_px"] == 9000
    assert result["elements"][0]["type"] == "rect"
