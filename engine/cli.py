"""Command-line entry point for the first local end-to-end workflow."""
from __future__ import annotations
import argparse
import asyncio
import json
from pathlib import Path
from typing import Any
from agents.contracts import DesignJob
from agents.mock_backend import MockBackend
from agents.orchestrator import DesignOrchestrator
from engine.exporters import export_artwork
from engine.profiles import list_profiles, load_profile
from engine.svg import render_preview


def _read_job(path: str) -> DesignJob:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return DesignJob(**data)


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(prog="bottle-agent", description="Bottle artwork rev0.1 CLI")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("profiles", help="List supported bottle profiles")
    validate = sub.add_parser("validate", help="Validate a job manifest and profile")
    validate.add_argument("job", help="Path to job JSON")
    preview = sub.add_parser("preview", help="Run offline mock agents and render a preview")
    preview.add_argument("job", help="Path to job JSON")
    preview.add_argument("--output", default="output/preview.png")
    export = sub.add_parser("export", help="Render production-size files after explicit approval")
    export.add_argument("job", help="Path to job JSON")
    export.add_argument("--output-dir", default="output")
    export.add_argument("--approve", action="store_true", help="Explicitly approve production-size export")
    args = parser.parse_args()
    if args.command == "profiles":
        print(json.dumps(list_profiles(), indent=2))
        return
    if args.command == "validate":
        job = _read_job(args.job)
        profile = load_profile(job.profile_id)
        if not job.theme.strip():
            parser.error("theme must not be empty")
        print(json.dumps({"valid": True, "theme": job.theme, "profile": profile}, indent=2))
        return
    job = _read_job(args.job)
    state = asyncio.run(DesignOrchestrator(MockBackend()).prepare(job))
    if state.blocked:
        raise SystemExit(f"Design blocked: {state.block_reason}")
    if args.command == "preview":
        target = render_preview(state.layout_spec, state.profile, args.output)
        report = Path(args.output).with_suffix(".report.json")
        _write_json(report, {"job": job.to_dict(), "history": state.history,
            "quality_report": state.quality_report, "preview": str(target),
            "notice": "Mock backend output; no AI image analysis was performed."})
        print(f"Preview: {target}\nReport: {report}")
        return
    if args.command == "export":
        if not args.approve:
            raise SystemExit("Refusing production export. Review a preview, then pass --approve.")
        result = export_artwork(state.layout_spec, state.profile, args.output_dir)
        report = Path(args.output_dir) / f"{state.profile['id']}.export-report.json"
        _write_json(report, result)
        print(json.dumps(result, indent=2))
        print(f"Report: {report}")


if __name__ == "__main__":
    main()
