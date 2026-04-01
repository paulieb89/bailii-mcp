# BAILII MCP Server

Local MCP server for UK case law on BAILII. Search judgments, retrieve full text with section extraction. Runs locally because BAILII blocks cloud/datacenter IPs.

Covers UKSC, EWCA, EWHC, Upper Tribunal, EAT, First-tier Tribunal, and more.

## Why Local?

BAILII blocks requests from cloud servers (Fly.io, AWS, etc.) — they return 403 on all CGI endpoints. This server runs on your machine, so requests go through your residential IP.

## Setup

### Claude Desktop (quickest)

```bash
git clone https://github.com/paulieb89/bailii-mcp.git
cd bailii-mcp
pip install fastmcp httpx beautifulsoup4
fastmcp install claude-desktop server.py
```

That's it. Restart Claude Desktop and the BAILII tools appear automatically.

### Claude Code

```bash
git clone https://github.com/paulieb89/bailii-mcp.git
claude mcp add bailii -- python /full/path/to/bailii-mcp/server.py --stdio
```

### Manual config (.mcp.json or claude_desktop_config.json)

```json
{
  "mcpServers": {
    "bailii": {
      "command": "python",
      "args": ["/full/path/to/bailii-mcp/server.py", "--stdio"]
    }
  }
}
```

### HTTP mode (for testing or other MCP clients)

```bash
python server.py
# Starts on http://localhost:8000/mcp
```

## Tools

| Tool | Description |
|---|---|
| `bailii_search` | Full-text search across all BAILII databases. Returns titles, citations, paths, and snippets. |
| `bailii_get_judgment` | Retrieve judgment text with section extraction. Defaults to summary + conclusions (~5000 chars). |
| `bailii_list_courts` | List available UK courts with codes and URL patterns. |

### Section Extraction

`bailii_get_judgment` parses judgment HTML into sections. Default returns only summary + conclusions to avoid flooding the context window.

```
# Default: summary + conclusions (5000 chars max)
bailii_get_judgment(path="/ew/cases/EWCA/Civ/2026/35.html")

# Specific section
bailii_get_judgment(path="...", section="discussion")
bailii_get_judgment(path="...", section="background")

# Full text (can be very large — 30-100KB)
bailii_get_judgment(path="...", section="all")

# Custom size limit
bailii_get_judgment(path="...", max_chars=10000)
```

Available sections: `summary`, `conclusions`, `held`, `discussion`, `background`

## Example

```
> Search BAILII for HMO licensing case law

Found 5 results:
1. Chinn v Hoilund-Carlsen [2026] UKUT 110 (LC) — rent repayment orders, deliberate breach of licensing
2. Luton Landlords v Luton Borough Council [2026] EWCA Civ 35 — licensing scheme judicial review
...

> Get the summary of the first case

SUMMARY: The Upper Tribunal considered rent repayment orders where a
non-professional landlord with a single property deliberately breached
HMO licensing requirements...

sections_found: ["summary", "background", "discussion", "conclusions"]
total_chars: 45,230
returned_chars: 4,800
```

## Also Available

For case law that doesn't need BAILII specifically, the [uk-legal-mcp](https://github.com/paulieb89/uk-legal-mcp) server provides case law search via the TNA Find Case Law API — hosted on Fly.io, no local setup needed.

This BAILII server is useful when you need:
- Employment tribunal decisions (EAT coverage is better on BAILII)
- Older cases not yet in the TNA database
- Specific courts or tribunals with better BAILII indexing

## Notes

- BAILII terms prohibit bulk downloading — use for targeted research
- Be reasonable with request rate
- For systematic access use TNA Find Case Law API instead (in uk-legal-mcp)
- Section extraction depends on judgment formatting — not all judgments have clear section headers

## Licence

Apache 2.0
