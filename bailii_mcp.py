"""
bailii_mcp - Local MCP server for BAILII case law access.

Run from your own machine so requests go out via your residential IP,
bypassing BAILII's cloud IP blocks.

Usage:
    pip install bailii-mcp
    bailii-mcp --stdio

Or run the HTTP server:
    bailii-mcp
"""

import json
import re
from typing import Optional
from urllib.parse import quote, urljoin

import httpx
from bs4 import BeautifulSoup
from fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

BAILII_BASE = "https://www.bailii.org"
SEARCH_URL = "https://www.bailii.org/cgi-bin/lucy_search_1.cgi"
FORMAT_URL = "https://www.bailii.org/cgi-bin/format.cgi"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-GB,en;q=0.9",
}

# Courts available on BAILII - useful reference for users
COURT_CODES = {
    "UKSC": "UK Supreme Court",
    "UKHL": "House of Lords",
    "EWCA/Civ": "Court of Appeal (Civil)",
    "EWCA/Crim": "Court of Appeal (Criminal)",
    "EWHC": "High Court",
    "UKUT": "Upper Tribunal",
    "UKFTT": "First-tier Tribunal",
    "EAT": "Employment Appeal Tribunal",
}

# ---------------------------------------------------------------------------
# Server
# ---------------------------------------------------------------------------

mcp = FastMCP("bailii_mcp")


# ---------------------------------------------------------------------------
# Shared HTTP client helpers
# ---------------------------------------------------------------------------

async def _fetch_html(url: str, params: Optional[dict] = None) -> str:
    """Fetch a URL and return raw HTML. Raises on HTTP errors."""
    async with httpx.AsyncClient(headers=HEADERS, timeout=30.0, follow_redirects=True) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response.text


def _html_to_text(html: str) -> str:
    """Strip HTML to clean readable text, preserving paragraph structure."""
    soup = BeautifulSoup(html, "html.parser")

    # Remove nav/header/footer noise
    for tag in soup.select("script, style, nav, header, footer, .navbar, #navbar"):
        tag.decompose()

    # Preserve paragraph breaks
    for tag in soup.find_all(["p", "br", "h1", "h2", "h3", "h4", "li"]):
        tag.insert_before("\n")
        tag.insert_after("\n")

    text = soup.get_text(separator=" ")
    # Collapse whitespace but keep paragraph breaks
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _handle_error(e: Exception) -> str:
    if isinstance(e, httpx.HTTPStatusError):
        if e.response.status_code == 403:
            return (
                "Error 403: BAILII blocked this request. "
                "Make sure you are running this server locally (not on a cloud/VPS IP). "
                "If you are running locally, wait a few minutes and try again."
            )
        if e.response.status_code == 404:
            return "Error 404: Page not found. Check the case citation or URL."
        return f"Error: HTTP {e.response.status_code} from BAILII."
    if isinstance(e, httpx.TimeoutException):
        return "Error: Request timed out. BAILII may be slow — try again."
    if isinstance(e, httpx.ConnectError):
        return "Error: Could not connect to BAILII. Check your internet connection."
    return f"Error: {type(e).__name__}: {e}"


# ---------------------------------------------------------------------------
# Input models
# ---------------------------------------------------------------------------

class SearchInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    query: str = Field(
        ...,
        description="Full-text search query, e.g. 'landlord HMO licensing duty of care'",
        min_length=2,
        max_length=500,
    )
    max_results: int = Field(
        default=10,
        description="Maximum number of results to return (1-30)",
        ge=1,
        le=30,
    )


class GetJudgmentInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    path: str = Field(
        ...,
        description=(
            "BAILII document path, e.g. '/ew/cases/EWCA/Civ/2011/554.html'. "
            "Obtain this from bailii_search results."
        ),
        min_length=5,
    )
    section: Optional[str] = Field(
        default=None,
        description=(
            "Return only a specific section of the judgment. Common values: "
            "'summary', 'conclusions', 'held', 'discussion', 'background', 'all'. "
            "Default (None) returns summary + conclusions if found, or first 5000 chars. "
            "Use 'all' to get the full text (can be very large)."
        ),
    )
    max_chars: Optional[int] = Field(
        default=None,
        description="Maximum characters to return. Default 5000 unless section='all'. Increase if you need more context.",
        ge=500,
        le=200000,
    )


class GetByNeutralCitationInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    neutral_citation: str = Field(
        ...,
        description=(
            "Neutral citation string, e.g. '[2024] UKSC 12' or '[2019] EWCA Civ 1'."
        ),
        min_length=5,
        max_length=100,
    )


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

@mcp.tool(
    name="bailii_search",
    annotations={
        "title": "Search BAILII Case Law",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def bailii_search(params: SearchInput) -> str:
    """Search BAILII for UK case law by keyword or phrase.

    Searches the full BAILII database including UKSC, EWCA, EWHC, House of Lords,
    tribunals, and Irish courts. Returns a list of matching cases with titles,
    citations, and document paths to use with bailii_get_judgment.

    Args:
        params (SearchInput): Search parameters containing:
            - query (str): Search terms
            - max_results (int): Number of results to return (default 10)

    Returns:
        str: JSON array of results, each containing:
            {
                "title": str,
                "path": str,      # pass to bailii_get_judgment
                "url": str,
                "snippet": str
            }
    """
    try:
        html = await _fetch_html(
            SEARCH_URL,
            params={
                "query": params.query,
                "method": "boolean",
                "results": str(params.max_results),
                "sort": "date",
            },
        )
    except Exception as e:
        return _handle_error(e)

    soup = BeautifulSoup(html, "html.parser")
    results = []

    # BAILII search results are in <dt>/<dd> pairs or <li> elements
    for link in soup.select("a[href]"):
        href = link.get("href", "")
        # Filter to case law paths only
        if "/cases/" not in href:
            continue
        if not href.endswith(".html"):
            continue

        title = link.get_text(strip=True)
        if not title or len(title) < 5:
            continue

        # Grab snippet from surrounding text
        parent = link.find_parent()
        snippet = parent.get_text(strip=True)[:300] if parent else ""

        # Normalise path
        if href.startswith("http"):
            path = href.replace(BAILII_BASE, "")
            url = href
        else:
            path = href
            url = urljoin(BAILII_BASE, href)

        results.append({
            "title": title,
            "path": path,
            "url": url,
            "snippet": snippet,
        })

        if len(results) >= params.max_results:
            break

    if not results:
        return json.dumps({
            "query": params.query,
            "count": 0,
            "results": [],
            "note": "No results found. Try broader search terms.",
        }, indent=2)

    return json.dumps({
        "query": params.query,
        "count": len(results),
        "results": results,
    }, indent=2)


@mcp.tool(
    name="bailii_get_judgment",
    annotations={
        "title": "Get BAILII Judgment Text",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def bailii_get_judgment(params: GetJudgmentInput) -> str:
    """Retrieve a BAILII judgment, optionally filtered to a specific section.

    Use the path returned by bailii_search. By default returns summary +
    conclusions (or first 5000 chars if no sections detected). Use section='all'
    for the complete text.

    Args:
        params (GetJudgmentInput): Input containing:
            - path (str): BAILII document path
            - section (str, optional): 'summary', 'conclusions', 'held', 'discussion', 'background', 'all'
            - max_chars (int, optional): Maximum characters to return (default 5000)

    Returns:
        str: JSON object with path, url, title, sections_found, and text.
    """
    path = params.path.strip()
    if not path.startswith("/"):
        path = "/" + path

    url = f"{FORMAT_URL}?doc={path}"

    try:
        html = await _fetch_html(url)
    except Exception as e:
        return _handle_error(e)

    soup = BeautifulSoup(html, "html.parser")

    title = ""
    title_tag = soup.find("title")
    if title_tag:
        title = title_tag.get_text(strip=True)

    for tag in soup.select("script, style, nav, .navbar, #navbar, form"):
        tag.decompose()

    body = soup.find("body")
    text = _html_to_text(str(body)) if body else _html_to_text(str(soup))

    lines = text.splitlines()
    cleaned = [
        line for line in lines
        if not re.match(r"^\s*(BAILII|Copyright|Feedback|Donate|URL:)\s*", line)
    ]
    full_text = "\n".join(cleaned).strip()

    # Parse sections from the judgment text
    section_patterns = {
        "summary": re.compile(r"\bSUMMARY\b", re.IGNORECASE),
        "background": re.compile(r"\bBACKGROUND\b|\bINTRODUCTION\b|\bFACTS\b", re.IGNORECASE),
        "discussion": re.compile(r"\bDISCUSSION\b|\bANALYSIS\b|\bREASONS\b", re.IGNORECASE),
        "conclusions": re.compile(r"\bCONCLUSIONS?\b|\bHELD\b|\bDECISION\b|\bORDER\b", re.IGNORECASE),
        "held": re.compile(r"\bHELD\b", re.IGNORECASE),
    }

    sections_found = {}
    section_lines = full_text.splitlines()

    for sec_name, pattern in section_patterns.items():
        for i, line in enumerate(section_lines):
            stripped = line.strip()
            if len(stripped) < 80 and pattern.search(stripped):
                # Found a section header — grab text until next section header or end
                start = i + 1
                end = len(section_lines)
                for j in range(start + 1, len(section_lines)):
                    next_line = section_lines[j].strip()
                    if len(next_line) < 80 and any(
                        p.search(next_line) for p in section_patterns.values()
                    ) and j > start + 2:
                        end = j
                        break
                section_text = "\n".join(section_lines[start:end]).strip()
                if section_text and len(section_text) > 50:
                    sections_found[sec_name] = section_text
                break

    # Determine what to return
    requested_section = (params.section or "").lower().strip()
    default_max = 5000

    if requested_section == "all":
        output_text = full_text
        default_max = 200000
    elif requested_section and requested_section in sections_found:
        output_text = sections_found[requested_section]
    elif requested_section:
        output_text = f"Section '{requested_section}' not found. Available sections: {', '.join(sections_found.keys()) or 'none detected'}.\n\n" + full_text[:default_max]
    else:
        # Default: summary + conclusions, or first N chars
        parts = []
        if "summary" in sections_found:
            parts.append("SUMMARY\n" + sections_found["summary"])
        if "conclusions" in sections_found:
            parts.append("CONCLUSIONS\n" + sections_found["conclusions"])
        if "held" in sections_found and "conclusions" not in sections_found:
            parts.append("HELD\n" + sections_found["held"])

        if parts:
            output_text = "\n\n---\n\n".join(parts)
        else:
            output_text = full_text[:default_max]

    max_chars = params.max_chars or default_max
    truncated = len(output_text) > max_chars
    output_text = output_text[:max_chars]

    return json.dumps({
        "path": path,
        "url": url,
        "title": title,
        "sections_found": list(sections_found.keys()),
        "truncated": truncated,
        "total_chars": len(full_text),
        "returned_chars": len(output_text),
        "text": output_text,
    }, indent=2)


@mcp.tool(
    name="bailii_list_courts",
    annotations={
        "title": "List Available BAILII Courts",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def bailii_list_courts() -> str:
    """List the main UK courts and tribunals available on BAILII.

    Returns court codes useful for constructing direct BAILII URLs or
    understanding search results.

    Returns:
        str: JSON object mapping court codes to court names.
    """
    return json.dumps({
        "courts": COURT_CODES,
        "note": (
            "BAILII URL pattern: https://www.bailii.org/ew/cases/{COURT}/{YEAR}/{NUMBER}.html "
            "e.g. https://www.bailii.org/uk/cases/UKSC/2024/1.html"
        ),
    }, indent=2)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    import os, sys
    if "--stdio" in sys.argv:
        mcp.run()
    else:
        port = int(os.getenv("PORT", "8000"))
        print(f"Starting bailii_mcp on http://localhost:{port}")
        print(f"Add http://localhost:{port}/mcp as a connector in Claude desktop.")
        mcp.run(transport="streamable-http", host="127.0.0.1", port=port)


if __name__ == "__main__":
    main()
