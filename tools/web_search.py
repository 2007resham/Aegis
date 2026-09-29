import requests
import config


def web_search(query: str, max_results: int = 5) -> str:
    """Search the web via SerpAPI and return a compact summary of top results."""
    if not config.SERPAPI_API_KEY:
        return "Web search is not configured. Add SERPAPI_API_KEY to your .env file."

    try:
        resp = requests.get(
            "https://serpapi.com/search",
            params={
                "q": query,
                "api_key": config.SERPAPI_API_KEY,
                "num": max_results,
            },
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        return f"Web search failed: {e}"

    parts = []

    # SerpAPI sometimes returns a direct answer box for simple queries
    if "answer_box" in data:
        box = data["answer_box"]
        answer = box.get("answer") or box.get("snippet") or box.get("result")
        if answer:
            parts.append(f"Quick answer: {answer}")

    for r in data.get("organic_results", [])[:max_results]:
        title = r.get("title", "Untitled")
        link = r.get("link", "")
        snippet = r.get("snippet", "")
        parts.append(f"- {title} ({link}): {snippet}")

    return "\n".join(parts) if parts else "No results found."