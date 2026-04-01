# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

bailii-mcp is a local MCP server that gives Claude access to BAILII (British and Irish Legal Information Institute) case law. It must run locally because BAILII blocks cloud/datacenter IPs.

Single-file server: all logic lives in `server.py` (~445 lines). No package structure, no test suite.

## Running

```bash
# Install dependencies (Python 3.10+)
pip install fastmcp httpx beautifulsoup4

# Run in stdio mode (Claude Desktop / Claude Code)
python3 server.py --stdio

# Run as HTTP server for local dev/testing
python3 server.py              # default port 8000
PORT=9000 python3 server.py    # custom port
```

## Architecture

**Framework**: FastMCP — tools registered via `@mcp.tool()` decorators with Pydantic input models.

**Three tools**:
- `bailii_search` — full-text search, returns JSON with title/path/url/snippet
- `bailii_get_judgment` — fetches judgment HTML, parses into sections (summary, background, discussion, conclusions, held), returns targeted or full text
- `bailii_list_courts` — static reference data (8 UK court codes)

**Data flow**: HTTP request (httpx async) → BAILII website → BeautifulSoup HTML parsing → section detection via regex → JSON response.

**Section extraction**: Detects headers by matching short lines (<80 chars) against regex patterns. Returns summary + conclusions by default, or a specific section on request. Falls back to first 5000 chars if no sections detected.

**Entry point**: `__main__` block checks for `--stdio` flag — stdio mode for MCP protocol, HTTP mode otherwise.

## Key constraints

- BAILII terms prohibit bulk downloading — tool is for targeted research only
- 403 errors usually mean the server is running on a cloud IP instead of locally
- No pyproject.toml or setup.py — dependencies declared in `fastmcp.json` only
- The `.mcpb` bundle is a pre-built ZIP for one-click Claude Desktop install
