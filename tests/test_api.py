"""End-to-end API behaviour, exercised against the offline mock backend."""
from __future__ import annotations

import time

import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402

from api.app import JOBS, JobState, app  # noqa: E402

client = TestClient(app)


@pytest.fixture(autouse=True)
def _clean_jobs():
    JOBS.clear()
    yield
    JOBS.clear()


def _wait(job_id: str, timeout: float = 30.0) -> dict:
    deadline = time.time() + timeout
    terminal = {JobState.PREVIEW_READY, JobState.COMPLETE,
                JobState.BLOCKED, JobState.FAILED}
    while time.time() < deadline:
        body = client.get(f"/jobs/{job_id}").json()
        if body["state"] in {s.value for s in terminal}:
            return body
        time.sleep(0.05)
    raise AssertionError(f"job {job_id} did not settle: {body}")


def test_health_reports_routing():
    body = client.get("/health").json()
    assert body["status"] == "ok"
    assert "routing" in body["model_routing"]
    assert body["profiles"] == 5


def test_profiles_are_listed():
    ids = {p["id"] for p in client.get("/profiles").json()}
    assert {"fat_250ml", "fat_500ml", "fat_1l", "long_500ml", "long_1l"} <= ids


def test_unknown_profile_is_rejected():
    r = client.post("/jobs", json={"theme": "x", "profile_id": "nope"})
    assert r.status_code == 422


def test_blank_theme_is_rejected():
    r = client.post("/jobs", json={"theme": "   ", "profile_id": "fat_500ml"})
    assert r.status_code == 422


def test_job_runs_to_preview_and_serves_the_file():
    r = client.post("/jobs", json={
        "theme": "Baby shower", "profile_id": "fat_500ml",
        "required_text": ["BPA FREE"]})
    assert r.status_code == 202
    job_id = r.json()["id"]

    body = _wait(job_id)
    assert body["state"] == JobState.PREVIEW_READY.value, body
    assert body["report"]["model_routing"]["using_mock"] is True
    assert "preview.png" in body["files"]

    f = client.get(f"/jobs/{job_id}/files/preview.png")
    assert f.status_code == 200
    assert len(f.content) > 0


def test_report_derives_servings_from_capacity():
    r = client.post("/jobs", json={"theme": "t", "profile_id": "fat_250ml"})
    body = _wait(r.json()["id"])
    assert body["report"]["servings_per_container"] == "about 1"

    r2 = client.post("/jobs", json={"theme": "t", "profile_id": "fat_500ml"})
    body2 = _wait(r2.json()["id"])
    assert body2["report"]["servings_per_container"] == "about 2"


def test_missing_components_block_rather_than_fail():
    r = client.post("/jobs", json={
        "theme": "t", "profile_id": "fat_500ml",
        "components": ["definitely_not_a_component"]})
    body = _wait(r.json()["id"])
    assert body["state"] == JobState.BLOCKED.value
    assert "definitely_not_a_component" in body["message"]


def test_preview_first_is_the_default():
    r = client.post("/jobs", json={"theme": "t", "profile_id": "fat_500ml"})
    assert r.json()["request"]["auto_export"] is False
    body = _wait(r.json()["id"])
    assert body["state"] == JobState.PREVIEW_READY.value
    assert "export" not in (body["report"] or {})


def test_path_traversal_is_refused():
    r = client.post("/jobs", json={"theme": "t", "profile_id": "fat_500ml"})
    job_id = r.json()["id"]
    _wait(job_id)
    assert client.get(f"/jobs/{job_id}/files/..%2F..%2Fpyproject.toml").status_code == 404


def test_unknown_job_is_404():
    assert client.get("/jobs/deadbeef").status_code == 404
    assert client.delete("/jobs/deadbeef").status_code == 404


def test_delete_removes_the_job():
    r = client.post("/jobs", json={"theme": "t", "profile_id": "fat_500ml"})
    job_id = r.json()["id"]
    _wait(job_id)
    assert client.delete(f"/jobs/{job_id}").status_code == 204
    assert client.get(f"/jobs/{job_id}").status_code == 404
