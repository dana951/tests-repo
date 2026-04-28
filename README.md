# tests-repo

This repository is part of the larger [`eks-gitops-platform`](https://github.com/dana951/eks-gitops-platform) project.

Its purpose is to demonstrate a test automation suite that runs as part of a CI/CD pipeline.
The suite includes API and smoke tests that validate deployed services quickly and consistently across environments.

## How to use

1. Install dependencies:

```bash
uv sync
```

2. Run smoke tests (fast checks):

```bash
uv run pytest -m smoke -v --env=dev
```

3. Run API tests:

```bash
uv run pytest -m api -v --env=dev
```

4. Run against a local URL override (optional):

```bash
uv run pytest -m smoke -v --env=dev --base-url=http://localhost:8080
```

### Common options

- `--env`: target Kubernetes namespace/environment (for example: `dev`, `qa`, `staging`, `prod`)
- `--base-url`: optional full URL override instead of in-cluster DNS
- `--expected-version`: optional deployment version check used by version tests

