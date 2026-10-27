"""Wikipedia tool — search and short summary via the public Wikipedia API."""

import requests

SEARCH_URL = "https://en.wikipedia.org/w/api.php"
SUMMARY_URL = "https://en.wikipedia.org/api/rest_v1/page/summary/{}"
HEADERS = {"User-Agent": "mogzauri-agent/0.1 (university AI course project)"}


def search_wikipedia(query: str) -> str:
    """
    Look up a place, landmark or topic on Wikipedia and return a short summary.

    Args:
        query: What to search for (e.g. "Gergeti Trinity Church", "Svaneti").

    Returns:
        The article title and a short summary paragraph,
        or an error message starting with "ERROR".
    """
    try:
        search = requests.get(SEARCH_URL, headers=HEADERS, timeout=10, params={
            "action": "query", "list": "search", "srsearch": query,
            "srlimit": 1, "format": "json",
        }).json()
        hits = search["query"]["search"]
        if not hits:
            return f"ERROR: nothing found on Wikipedia for '{query}'."
        title = hits[0]["title"]
        summary = requests.get(SUMMARY_URL.format(title.replace(" ", "_")),
                               headers=HEADERS, timeout=10).json()
    except requests.RequestException as e:
        return f"ERROR: Wikipedia unavailable ({e})."
    return f"{title}: {summary.get('extract', 'no summary available')}"
