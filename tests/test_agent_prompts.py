from agents.runtime import build_agent_definitions, SpecialistAgent


class UnusedBackend:
    async def complete_json(self, **kwargs):
        raise AssertionError("Backend should not be called by prompt loading test")


def test_every_registered_agent_has_a_nonempty_prompt():
    for definition in build_agent_definitions():
        prompt = SpecialistAgent(definition, UnusedBackend()).system_prompt()
        assert prompt.strip()
