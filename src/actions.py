import requests

def unsubscribe(link):
    """Hit a single unsubscribe URL and return (status_code, response_text)."""
    try:
        resp = requests.get(link, timeout=10)
        return resp.status_code, resp.text[:200]  # truncate body for logging
    except Exception as e:
        return None, str(e)

def bulk_unsubscribe(links):
    """Given an iterable of URLs, unsubscribe from each and collect results."""
    results = {}
    for link in links:
        status, info = unsubscribe(link)
        results[link] = {'status': status, 'info': info}
    return results
