# Specialist agent system

The first executable multi-agent layer is provider-neutral: `runtime.py` defines an `AgentBackend` protocol and loads one system prompt per specialist. A provider adapter can be added without changing the agent contracts or workflow.

## Implemented specialists

1. **Image analysis** — describes supplied references and flags asset quality concerns.
2. **Theme planner** — turns the theme into a visual hierarchy and creative direction.
3. **Asset placement** — plans positions for user-approved content and reports missing assets.
4. **Layout** — returns a compact, normalized vector layout specification for the deterministic renderer.
5. **Quality review** — checks requirements and blocks unsafe/incomplete jobs.
6. **Export coordinator** — defined in `prompts/export.md`; invoked by the deterministic export service after approval.
7. **Orchestrator** — coordinates the pipeline and enforces preview/final-export approval boundaries.

## Contracts and execution

- `contracts.py` defines `DesignJob` and `PipelineState`.
- `runtime.py` defines `AgentBackend`, `SpecialistAgent`, and the agent registry.
- `orchestrator.py` runs the specialist sequence asynchronously.
- Agent outputs must be JSON objects and pass required-field checks.
- Asset data is represented by IDs and file paths. Full-resolution image bytes are not passed between agents.
- Final rendering/export are injected deterministic services, not LLM-generated files.

## Current limitation

No model-provider adapter is configured yet. The framework is ready for one, but the agents do not run autonomously until an adapter is implemented and credentials/configuration are supplied by the deployment environment. Do not put API keys in this repository.
