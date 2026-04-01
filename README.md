# bailii_mcp

Local MCP server for BAILII case law.

## Setup

```bash
pip install fastmcp httpx beautifulsoup4
```

Then configure your MCP client with:

```json
{
  "mcpServers": {
    "bailii": {
      "command": "/home/bch/company/bouch-pages/idea/.venv/bin/python",
      "args": ["/home/bch/company/bouch-pages/idea/server.py", "--stdio"]
    }
  }
}
```

## Tools

| Tool | Description |
|---|---|
| `bailii_search` | Full-text search across all BAILII databases |
| `bailii_get_judgment` | Fetch full judgment text by path |
| `bailii_list_courts` | List available courts and URL patterns |

## Notes

- Be polite with request rate - add delays if fetching many judgments
- BAILII terms prohibit bulk downloading; use for targeted research
- For systematic case law access use TNA Find Case Law API instead
  (already in uk-legal-mcp as `case_law_search`)
