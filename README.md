# BAILII MCP Server

<!-- mcp-name: io.github.paulieb89/bailii-mcp -->

Search UK case law on BAILII. Retrieve judgments with automatic section extraction (summary, conclusions, discussion, background). Runs locally — BAILII blocks cloud IPs.

## Install

### Using uv (recommended)

No install needed — [`uvx`](https://docs.astral.sh/uv/) runs it directly from PyPI:

```bash
uvx bailii-mcp
```

### Using pip

```bash
pip install bailii-mcp
bailii-mcp
```

Requires Python 3.10+.

## Configuration

### Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "bailii": {
      "command": "uvx",
      "args": ["bailii-mcp"]
    }
  }
}
```

### Claude Code

```bash
claude mcp add bailii -- uvx bailii-mcp
```

### VS Code

Add to `.vscode/settings.json` or use the MCP panel:

```json
{
  "mcp": {
    "servers": {
      "bailii": {
        "command": "uvx",
        "args": ["bailii-mcp"]
      }
    }
  }
}
```

### Using pip instead of uvx

If you installed via `pip install bailii-mcp`, use `"command": "bailii-mcp"` and `"args": []` instead.

### From source

```bash
git clone https://github.com/paulieb89/bailii-mcp.git
cd bailii-mcp
pip install -e .
```

## What You Can Ask

Once connected, just ask Claude naturally:

- "Search BAILII for cases about HMO licensing"
- "Find recent whistleblowing employment tribunal cases"
- "Get the summary of Chinn v Hoilund-Carlsen"
- "What did the court hold in that case?"
- "Show me the discussion section"

## Tools

| Tool | What it does |
|------|-------------|
| `bailii_search` | Full-text search across all BAILII courts. Returns titles, citations, and links. |
| `bailii_get_judgment` | Retrieve judgment text. Defaults to summary + conclusions (~5000 chars). |
| `bailii_list_courts` | List available UK courts (UKSC, EWCA, EWHC, UKUT, EAT, etc). |

### Section Extraction

Judgments are large (30-100KB). By default, only the summary and conclusions are returned. Ask for more if you need it:

- **Default**: summary + conclusions (5000 chars)
- **Specific section**: "show me the discussion" → pulls just that section
- **Full text**: "get the complete judgment" → returns everything

Sections detected: `summary`, `conclusions`, `held`, `discussion`, `background`

## Why Local?

BAILII blocks requests from cloud servers and datacenters. This server runs on your machine, so requests go through your residential IP.

For case law that doesn't need BAILII specifically, [uk-legal-mcp](https://github.com/paulieb89/uk-legal-mcp) provides case law via the National Archives API — hosted on Fly.io, no local setup needed.

This BAILII server is useful when you need:
- Employment tribunal decisions (EAT coverage is stronger on BAILII)
- Older cases not yet in the TNA database
- Specific tribunals with better BAILII indexing

## Notes

- BAILII terms prohibit bulk downloading — use for targeted research only
- Be reasonable with request rate
- Section extraction depends on judgment formatting — not all judgments have clear section headers

## Licence

Apache 2.0

## Author

[Paul Boucherat](https://bouch.dev) — building MCP servers for UK property, legal, and project controls.
