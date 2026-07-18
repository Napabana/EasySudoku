"""Production-safety API tests for the hackathon submission."""

from __future__ import annotations

import io
import tempfile
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

import main


client = TestClient(main.app)


def test_health_and_version_do_not_leak_paths() -> None:
    health = client.get("/health")
    assert health.status_code == 200
    assert set(health.json()) == {
        "status",
        "frontend_build_available",
        "ocr_model_available",
        "application_version",
    }

    version = client.get("/version")
    assert version.status_code == 200
    assert set(version.json()) == {"version", "git_commit"}
    payload = f"{health.text} {version.text}"
    assert str(main.BASE_DIR) not in payload
    assert "MAX_UPLOAD_BYTES" not in payload


def test_missing_frontend_is_explicit_and_legacy_is_opt_in() -> None:
    missing = Path(tempfile.gettempdir()) / "easysudoku-missing-index.html"
    with patch.object(main, "FRONTEND_INDEX", missing), patch.object(main, "ALLOW_LEGACY_FRONTEND", False):
        response = client.get("/")
        assert response.status_code == 503
        assert response.json()["detail"]["code"] == "FRONTEND_BUILD_MISSING"

    with patch.object(main, "FRONTEND_INDEX", missing), patch.object(main, "ALLOW_LEGACY_FRONTEND", True):
        response = client.get("/")
        assert response.status_code == 200
        assert "EasySudoku" in response.text


def test_api_like_missing_routes_are_not_spa_fallbacks() -> None:
    for path in ("/api/missing", "/upload/missing", "/next-step/missing"):
        response = client.get(path)
        assert response.status_code == 404
        assert response.headers["content-type"].startswith("application/json")


def test_upload_validation() -> None:
    response = client.post("/upload", files={"file": ("notes.txt", b"not an image", "text/plain")})
    assert response.status_code == 415
    assert response.json()["detail"]["code"] == "UNSUPPORTED_MEDIA_TYPE"

    response = client.post("/upload", files={"file": ("empty.png", b"", "image/png")})
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "EMPTY_FILE"

    with patch.object(main, "MAX_UPLOAD_BYTES", 4):
        response = client.post("/upload", files={"file": ("large.png", b"12345", "image/png")})
    assert response.status_code == 413
    assert response.json()["detail"]["code"] == "FILE_TOO_LARGE"


def test_upload_demo_fixture() -> None:
    image = Path("examples/demo_sudoku.png").read_bytes()
    expected = Path("examples/demo_grid.json").read_text(encoding="utf-8").strip()
    response = client.post("/upload", files={"file": ("demo_sudoku.png", io.BytesIO(image), "image/png")})
    assert response.status_code == 200
    assert response.json()["grid"] == __import__("json").loads(expected)


if __name__ == "__main__":
    tests = [
        test_health_and_version_do_not_leak_paths,
        test_missing_frontend_is_explicit_and_legacy_is_opt_in,
        test_api_like_missing_routes_are_not_spa_fallbacks,
        test_upload_validation,
        test_upload_demo_fixture,
    ]
    for test in tests:
        test()
        print(f"PASS: {test.__name__}")
