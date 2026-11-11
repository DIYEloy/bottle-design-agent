"""Small, provider-neutral data contracts shared by the agent pipeline."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class AgentResult:
    agent: str
    status: str
    data: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class DesignJob:
    """User-approved job inputs. Asset paths refer to files managed outside prompts."""

    theme: str
    profile_id: str
    reference_assets: list[str] = field(default_factory=list)
    approved_assets: list[str] = field(default_factory=list)
    required_text: list[str] = field(default_factory=list)
    optional_elements: list[str] = field(default_factory=list)
    notes: str = ""
    black_and_white_only: bool = True
    dpi: int = 1200

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class PipelineState:
    job: DesignJob
    profile: dict[str, Any]
    image_analysis: dict[str, Any] = field(default_factory=dict)
    creative_brief: dict[str, Any] = field(default_factory=dict)
    asset_plan: dict[str, Any] = field(default_factory=dict)
    layout_spec: dict[str, Any] = field(default_factory=dict)
    quality_report: dict[str, Any] = field(default_factory=dict)
    history: list[dict[str, Any]] = field(default_factory=list)
    blocked: bool = False
    block_reason: str | None = None

    def compact_context(self) -> dict[str, Any]:
        """Return references and decisions, never embedded full-resolution image bytes."""
        return {
            "job": self.job.to_dict(),
            "profile": self.profile,
            "image_analysis": self.image_analysis,
            "creative_brief": self.creative_brief,
            "asset_plan": self.asset_plan,
            "layout_spec": self.layout_spec,
            "quality_report": self.quality_report,
        }
