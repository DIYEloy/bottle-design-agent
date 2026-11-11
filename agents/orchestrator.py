"""Coordinates specialist agents while keeping preview approval explicit."""
from __future__ import annotations

from typing import Any, Callable

from agents.contracts import DesignJob, PipelineState
from agents.runtime import AgentBackend, build_agents
from engine.profiles import load_profile


class DesignOrchestrator:
    """Runs analysis → concept → assets → layout → quality.

    A preview renderer and final exporter are injected deterministic services.
    The orchestrator never sends raster bytes to an LLM.
    """

    def __init__(
        self,
        backend: AgentBackend,
        preview_renderer: Callable[[dict[str, Any], dict[str, Any]], str] | None = None,
        final_exporter: Callable[[dict[str, Any], dict[str, Any]], dict[str, str]] | None = None,
    ):
        self.agents = build_agents(backend)
        self.preview_renderer = preview_renderer
        self.final_exporter = final_exporter

    async def prepare(self, job: DesignJob) -> PipelineState:
        if not job.theme.strip():
            raise ValueError("A design theme is required")
        if not job.black_and_white_only:
            raise ValueError("This project currently supports black-and-white artwork only")
        if job.dpi != 1200:
            raise ValueError("This project currently targets 1200 DPI")
        profile = load_profile(job.profile_id)
        state = PipelineState(job=job, profile=profile)

        image_result = await self.agents["image_analysis"].run({
            "theme": job.theme,
            "reference_assets": job.reference_assets,
            "approved_assets": job.approved_assets,
            "instruction": "Analyze supplied references; do not invent image contents. Use asset IDs/paths only."
        })
        state.image_analysis = image_result
        state.history.append({"agent": "image_analysis", "status": "complete"})

        creative = await self.agents["theme_planner"].run(state.compact_context())
        state.creative_brief = creative
        state.history.append({"agent": "theme_planner", "status": "complete"})

        assets = await self.agents["asset_placement"].run(state.compact_context())
        state.asset_plan = assets
        state.history.append({"agent": "asset_placement", "status": "complete"})
        if assets.get("missing_assets"):
            state.blocked = True
            state.block_reason = "Required user-approved assets or content are missing."
            return state

        layout = await self.agents["layout"].run(state.compact_context())
        state.layout_spec = layout
        state.history.append({"agent": "layout", "status": "complete"})

        quality = await self.agents["quality_review"].run(state.compact_context())
        state.quality_report = quality
        state.history.append({"agent": "quality_review", "status": "complete"})
        if not quality.get("passed", False):
            state.blocked = True
            state.block_reason = "Quality review did not pass."
        return state

    def render_preview(self, state: PipelineState) -> str:
        if state.blocked:
            raise RuntimeError(state.block_reason or "Pipeline is blocked")
        if self.preview_renderer is None:
            raise RuntimeError("No deterministic preview renderer has been configured")
        return self.preview_renderer(state.layout_spec, state.profile)

    def export_final(self, state: PipelineState, *, user_approved: bool) -> dict[str, str]:
        if not user_approved:
            raise PermissionError("Final-size export requires explicit user approval")
        if state.blocked:
            raise RuntimeError(state.block_reason or "Pipeline is blocked")
        if self.final_exporter is None:
            raise RuntimeError("No deterministic final exporter has been configured")
        return self.final_exporter(state.layout_spec, state.profile)
