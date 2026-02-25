from duckduckgo_search import DDGS

def search_web(query):
    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=3))
    return results