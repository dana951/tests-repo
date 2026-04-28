# e2e/test_smoke_e2e.py
#
# Smoke checks demonstrate fast validation in a CI/CD pipeline.
# Keep these tests minimal and safe for any environment.

from __future__ import annotations

import pytest
import requests

@pytest.mark.smoke
def test_root_serves_html(client: requests.Session) -> None:
    response = client.get("/")
    assert response.status_code == 200

@pytest.mark.smoke
def test_health_returns_ok(client: requests.Session) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}