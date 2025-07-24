import requests

def request_get(url, timeout=10):
    return requests.get(
        url,
        timeout=timeout,
    )