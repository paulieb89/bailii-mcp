# BAILII UK Case Law

## Tagline
Search UK court judgments on BAILII — runs locally because BAILII blocks cloud IPs.

## Description
BAILII UK Case Law gives AI agents direct access to the British and Irish Legal Information Institute (BAILII) — the largest free archive of UK court judgments. Search across UK Supreme Court, Court of Appeal, High Court, and specialist tribunals. Extract judgment text by section for clean, focused reading. Runs locally via `uvx` because BAILII blocks cloud IP ranges, so hosted MCP servers can't reach it. No API key required.

## Setup Requirements
No API keys or environment variables required. BAILII is free and open. This server runs **locally** on your machine via `uvx` — it cannot be hosted on Fly.io, Railway, or similar because BAILII blocks cloud provider IP ranges.

## Category
Education & Research

## Features
- Search UK case law across all BAILII-indexed courts (Supreme Court, Court of Appeal, High Court, First-tier Tribunal, Upper Tribunal, Employment Tribunal)
- Retrieve full judgment text for any case
- Extract specific numbered sections/paragraphs from a judgment for focused reading
- Covers England and Wales, Scotland, Northern Ireland, and Ireland
- Runs locally via `uvx bailii-mcp` — no cloud hosting needed
- Complements TNA Find Case Law (uk-legal-mcp) which has newer 2023+ judgments but not BAILII's deeper historical archive
- No API key required — BAILII is free and open
- Read-only — just queries BAILII's public pages

## Getting Started
- "Search BAILII for Supreme Court cases on landlord and tenant"
- "Find BAILII judgments citing Donoghue v Stevenson"
- "Pull the full text of [2024] UKSC 12 from BAILII"
- "Extract section 4 of the judgment in Caparo v Dickman"
- Tool: bailii_search — Search UK court judgments on BAILII
- Tool: bailii_get_judgment — Retrieve full judgment text
- Tool: bailii_get_section — Extract a specific numbered section from a judgment

## Tags
uk-law, case-law, bailii, court-judgments, supreme-court, legal-research, uk-legal, uk-courts, common-law, mcp, fastmcp, no-api-key, local-only, uvx

## Documentation URL
https://github.com/paulieb89/bailii-mcp
