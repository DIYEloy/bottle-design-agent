"""HTTP API for automated artwork generation.

Submit a job, poll it, download the artwork. Designed so a storefront, a form,
or another service can drive the pipeline without a human in the loop.

    pip install -e ".[api]"
    uvicorn api.app:app --reload

Endpoints
---------
``GET  /health``               liveness plus the active model routing
``GET  /profiles``             the supported bottle profiles
``GET  /components``           the component library inventory
``POST /jobs``                 submit a design job, returns a job id
``GET  /jobs``                 list jobs
``GET  /jobs/{id}``            job status and report
``GET  /jobs/{id}/files``      artifacts produced
``GET  /jobs/{id}/files/{name}`` download one artifact
``DELETE /jobs/{id}``          drop a job and its artifacts

Production notes
----------------
Jobs are held in memory and artifacts on local disk, which is fine for one
process and wrong for anything else. Before putting this behind real traffic,
move job state to a database and artifacts to object storage, and run the
pipeline on a task queue rather than in a background task. Rendering a
12000x6000 canvas is minutes of CPU and hundreds of MB of RAM, so it must not
share a process with the web workers.

There is no authentication here. Do not expose this to the internet as-is.
"""
from __future__ import annotations

import asyncio
import uuid
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, field_validator

from agents.contracts import DesignJob
from agents.orchestrator import DesignOrchestrator
from agents.tiered import build_backend
from engine.components import LIBRARY, servings_for_capacity
from engine.exporters import export_artwork
from engine.profiles import list_profiles, load_profile
from engine.svg import render_preview

OUTPUT_ROOT = Path("output") / "api"


class JobState(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    PREVIEW_READY = "preview_ready"
    EXPORTING = "exporting"
    COMPLETE = "complete"
    BLOCKED = "blocked"
    FAILED = "failed"


class JobRequest(BaseModel):
    theme: str = Field(min_length=1, max_length=500)
    profile_id: str
    required_text: list[str] = Field(default_factory=list, max_length=40)
    optional_elements: list[str] = Field(default_factory=list, max_length=40)
    reference_assets: list[str] = Field(default_factory=list, max_length=40)
    approved_assets: list[str] = Field(default_factory=list, max_length=40)
    components: list[str] = Field(default_factory=list, max_length=40,
                                  description="component slugs to place")
    notes: str = ""
    auto_export: bool = Field(
        default=False,
        description="Render production files without a human approving the "
                    "preview. Off by default: the house rule is preview first.",
    )

    @field_validator("profile_id")
    @classmethod
    def _known_profile(cls, v: str) -> str:
        known = {p["id"] for p in list_profiles()}
        if v not in known:
            raise ValueError(f"unknown profile_id {v!r}; known: {sorted(known)}")
        return v

    @field_validator("theme")
    @classmethod
    def _not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("theme must not be blank")
        return v


class JobRecord(BaseModel):
    id: str
    state: JobState
    created_at: datetime
    updated_at: datetime
    request: JobRequest
    message: str | None = None
    report: dict[str, Any] | None = None
    files: list[str] = Field(default_factory=list)


JOBS: dict[str, JobRecord] = {}

app = FastAPI(
    title="Bottle Design Agent",
    version="0.1.0",
    description="Automated black-and-white sublimation bottle artwork.",
)


def _touch(record: JobRecord, state: JobState, message: str | None = None) -> None:
    record.state = state
    record.updated_at = datetime.now(timezone.utc)
    if message is not None:
        record.message = message


def _job_dir(job_id: str) -> Path:
    return OUTPUT_ROOT / job_id


async def _run_job(job_id: str) -> None:
    record = JOBS.get(job_id)
    if record is None:
        return
    try:
        _touch(record, JobState.RUNNING)
        req = record.request

        missing = LIBRARY.missing(req.components) if req.components else []
        if missing:
            _touch(record, JobState.BLOCKED,
                   f"components not in the library: {missing}. "
                   "Run tools/extract_components.py.")
            return

        profile = load_profile(req.profile_id)
        job = DesignJob(
            theme=req.theme,
            profile_id=req.profile_id,
            reference_assets=req.reference_assets,
            approved_assets=req.approved_assets,
            required_text=req.required_text,
            optional_elements=req.optional_elements,
            notes=req.notes,
        )

        backend = build_backend()
        state = await DesignOrchestrator(backend).prepare(job)
        if state.blocked:
            _touch(record, JobState.BLOCKED, state.block_reason)
            return

        out = _job_dir(job_id)
        out.mkdir(parents=True, exist_ok=True)
        preview = render_preview(state.layout_spec, state.profile,
                                 str(out / "preview.png"))
        record.report = {
            "profile": profile,
            "servings_per_container": servings_for_capacity(
                profile.get("capacity_ml", 0) or 1),
            "quality_report": state.quality_report,
            "model_routing": backend.describe(),
            "model_calls": backend.call_log,
            "preview": str(preview),
            "notice": ("Mock backend output; no AI image analysis was performed."
                       if backend.describe()["using_mock"] else None),
        }
        record.files = sorted(p.name for p in out.iterdir() if p.is_file())
        _touch(record, JobState.PREVIEW_READY)

        if req.auto_export:
            _touch(record, JobState.EXPORTING)
            result = await asyncio.to_thread(
                export_artwork, state.layout_spec, state.profile, str(out))
            record.report["export"] = result
            record.files = sorted(p.name for p in out.iterdir() if p.is_file())
            _touch(record, JobState.COMPLETE)
    except Exception as exc:  # surface the failure rather than hanging
        _touch(record, JobState.FAILED, f"{type(exc).__name__}: {exc}")


# ---------------------------------------------------------------- endpoints
@app.get("/health")
def health() -> dict[str, Any]:
    backend = build_backend()
    return {
        "status": "ok",
        "model_routing": backend.describe(),
        "components_available": LIBRARY.available(),
        "profiles": len(list_profiles()),
    }


@app.get("/profiles")
def profiles() -> list[dict[str, Any]]:
    return list_profiles()


@app.get("/components")
def components() -> dict[str, Any]:
    if not LIBRARY.available():
        return {"available": False, "components": [],
                "hint": "run tools/extract_components.py <master.psd>"}
    return {"available": True, "components": LIBRARY.slugs()}


@app.post("/jobs", status_code=202)
def create_job(req: JobRequest, background: BackgroundTasks) -> JobRecord:
    now = datetime.now(timezone.utc)
    job_id = uuid.uuid4().hex[:12]
    record = JobRecord(id=job_id, state=JobState.QUEUED, created_at=now,
                       updated_at=now, request=req)
    JOBS[job_id] = record
    background.add_task(asyncio.run, _run_job(job_id))
    return record


@app.get("/jobs")
def list_jobs() -> list[JobRecord]:
    return sorted(JOBS.values(), key=lambda r: r.created_at, reverse=True)


@app.get("/jobs/{job_id}")
def get_job(job_id: str) -> JobRecord:
    record = JOBS.get(job_id)
    if record is None:
        raise HTTPException(404, f"no such job: {job_id}")
    return record


@app.get("/jobs/{job_id}/files")
def job_files(job_id: str) -> dict[str, Any]:
    record = JOBS.get(job_id)
    if record is None:
        raise HTTPException(404, f"no such job: {job_id}")
    return {"id": job_id, "state": record.state, "files": record.files}


@app.get("/jobs/{job_id}/files/{name}")
def job_file(job_id: str, name: str) -> FileResponse:
    if job_id not in JOBS:
        raise HTTPException(404, f"no such job: {job_id}")
    directory = _job_dir(job_id).resolve()
    target = (directory / name).resolve()
    if not str(target).startswith(str(directory) + "/") or not target.is_file():
        raise HTTPException(404, f"no such file: {name}")
    return FileResponse(target)


@app.delete("/jobs/{job_id}", status_code=204)
def delete_job(job_id: str) -> None:
    if JOBS.pop(job_id, None) is None:
        raise HTTPException(404, f"no such job: {job_id}")
    directory = _job_dir(job_id)
    if directory.exists():
        for child in directory.iterdir():
            child.unlink()
        directory.rmdir()
