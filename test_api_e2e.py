# API tests (the main E2E suite)
# e2e/test_api_e2e.py
#
# API E2E TESTS for deployed environments.
# This suite exists to demonstrate practical API validation in a
# CI/CD + GitOps portfolio workflow.
#
# Run examples:
#   In cluster namespace mode:
#     pytest e2e/test_api_e2e.py -v --env=dev
#   Local override mode:
#     pytest e2e/test_api_e2e.py -v --env=dev --base-url=http://localhost:8080

from __future__ import annotations

import pytest
import requests


# ── /health ───────────────────────────────────────────────────────────────────


@pytest.mark.api
@pytest.mark.e2e
def test_health_endpoint(client: requests.Session) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# ── /version ──────────────────────────────────────────────────────────────────


@pytest.mark.api
@pytest.mark.e2e
def test_version_response_shape(client: requests.Session) -> None:
    """Verify the response contains all expected fields with non-empty values."""
    response = client.get("/version")
    assert response.status_code == 200

    data = response.json()
    assert set(data.keys()) == {"version", "git_sha"}, (
        f"Unexpected keys in /version response: {data.keys()}"
    )
    assert data["version"], "version field should not be empty"
    assert data["git_sha"], "git_sha field should not be empty"


@pytest.mark.api
@pytest.mark.e2e
def test_version_matches_expected(
    client: requests.Session,
    expected_version: str,
) -> None:
    """
    When --expected-version is provided, assert the running app reports it.
    """
    if not expected_version:
        pytest.skip("--expected-version not set — skipping version assertion")

    response = client.get("/version")
    data = response.json()

    assert data["version"] == expected_version, (
        f"Deployed version mismatch. "
        f"Expected '{expected_version}', got '{data['version']}'. "
        f"The wrong image may be running."
    )


# ── /info ─────────────────────────────────────────────────────────────────────


@pytest.mark.api
@pytest.mark.e2e
def test_info_response_shape(client: requests.Session) -> None:
    response = client.get("/info")
    assert response.status_code == 200

    data = response.json()
    assert set(data.keys()) == {
        "hostname", "platform", "environment", "theme_color"
    }, f"Unexpected keys in /info response: {data.keys()}"


# ── /echo ─────────────────────────────────────────────────────────────────────


@pytest.mark.api
@pytest.mark.e2e
@pytest.mark.parametrize(
    ("params", "expected_status", "expected_message"),
    [
        ({"message": "e2e-test-ping"}, 200, "e2e-test-ping"),
        ({"message": ""}, 200, ""),
        ({}, 422, None),
    ],
    ids=["with-message", "empty-message", "missing-message"],
)
def test_echo_validation_cases(
    client: requests.Session,
    params: dict[str, str],
    expected_status: int,
    expected_message: str | None,
) -> None:
    response = client.get("/echo", params=params)
    assert response.status_code == expected_status

    data = response.json()
    if expected_status == 200:
        assert data["message"] == expected_message

