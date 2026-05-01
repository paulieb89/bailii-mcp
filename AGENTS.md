# AGENTS.md — bailii-mcp

AI agent instructions for working in this repo. See `/home/bch/dev/ops/OPS.md` for credentials, fleet overview, and release tooling.

## Repo shape

Single `bailii_mcp.py`. Wraps BAILII (British and Irish Legal Information Institute) for searching
UK case law and retrieving judgments with section extraction.
GitHub repo: `paulieb89/bailii-mcp`
Disk path: `/home/bch/dev/00_RELEASE/bailii-mcp/`

## Important: local-only by design

BAILII blocks cloud/datacenter IPs. This server runs on the user's machine using their residential
IP. Do NOT deploy to Fly.io or any cloud host — requests will be blocked.

Run locally via:
```bash
uvx bailii-mcp          # stdio (Claude Desktop / Claude Code)
uvx bailii-mcp --http   # HTTP mode for dev/testing (port 8000)
```

## Version bump

1. Update `version` in `pyproject.toml`
2. Update version string in the `smithery_server_card` route in `bailii_mcp.py`
3. Commit, tag `vX.Y.Z`, push + push tags
4. GitHub Actions publishes to PyPI automatically on tag

## Standard routes (HTTP mode only — fire on `--http` flag)

- `/.well-known/mcp/server-card.json` — Smithery metadata
- `/.well-known/glama.json` — Glama maintainer claim
- `/health` — health check

## Do not

- Do not deploy to Fly.io — BAILII blocks cloud IPs
- Do not commit credentials or session cookies
