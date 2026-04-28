# e2e/conftest.py
#
# Fixtures shared across all E2E test files.
#
# E2E tests target a REAL running deployment in Kubernetes.
# All runtime configuration is provided via pytest CLI options.
# We build the in-cluster DNS URL from the selected namespace.
#
# Local usage (point at a running instance):
#   pytest e2e/ -v --env=dev
#   pytest e2e/ -v --env=dev --base-url=http://localhost:8080

from __future__ import annotations

from urllib.parse import urljoin

import pytest
import requests

DEFAULT_SERVICE_NAME = "podinfo"
DEFAULT_SERVICE_PORT = "8080"


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--env",
        action="store",
        help="Target environment/namespace (example: dev, qa, staging, prod).",
    )
    parser.addoption(
        "--base-url",
        action="store",
        help="Optional full base URL override (example: http://localhost:8080).",
    )
    parser.addoption(
        "--service-name",
        action="store",
        default=DEFAULT_SERVICE_NAME,
        help=f"Kubernetes service name (default: {DEFAULT_SERVICE_NAME}).",
    )
    parser.addoption(
        "--service-port",
        action="store",
        default=DEFAULT_SERVICE_PORT,
        help=f"Kubernetes service port (default: {DEFAULT_SERVICE_PORT}).",
    )
    parser.addoption(
        "--expected-version",
        action="store",
        default="",
        help="Expected app version for deployment verification tests.",
    )


@pytest.fixture(scope="session")
def target_env(pytestconfig: pytest.Config) -> str:
    """
    Kubernetes namespace/environment under test.
    """
    env = (pytestconfig.getoption("--env") or "").strip().lower()
    if not env:
        pytest.fail("Missing required option --env. Example: pytest e2e/ --env=dev")
    return env


@pytest.fixture(scope="session")
def base_url(pytestconfig: pytest.Config, target_env: str) -> str:
    """
    Base URL of the live app under test.
    Priority:
      1) --base-url override (full URL)
      2) In-cluster DNS URL built from service + target namespace
    """
    explicit = (pytestconfig.getoption("--base-url") or "").strip().rstrip("/")
    if explicit:
        return explicit

    service_name = (
        pytestconfig.getoption("--service-name") or DEFAULT_SERVICE_NAME
    ).strip()
    service_port = (
        pytestconfig.getoption("--service-port") or DEFAULT_SERVICE_PORT
    ).strip()

    return f"http://{service_name}.{target_env}.svc.cluster.local:{service_port}"


@pytest.fixture(scope="session")
def expected_version(pytestconfig: pytest.Config) -> str:
    """
    The image tag / app version we just deployed.
    Passed as a CLI option so tests can assert the RIGHT version is running.
    """
    return (pytestconfig.getoption("--expected-version") or "").strip()


@pytest.fixture(scope="session")
def client(base_url: str) -> requests.Session:
    """
    Shared requests session for the whole E2E suite.
    Adds a thin helper to resolve relative paths against base_url.
    """
    session = requests.Session()
    session.headers.update({"Accept": "application/json"})

    original_get = session.get

    def get(path: str, **kwargs):
        timeout = kwargs.pop("timeout", 10.0)
        url = urljoin(f"{base_url}/", path.lstrip("/"))
        return original_get(url, timeout=timeout, **kwargs)

    session.get = get  # type: ignore[method-assign]
    try:
        yield session
    finally:
        session.close()