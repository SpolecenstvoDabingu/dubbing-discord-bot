import requests

def request_post(url, data=None, json=None, timeout=10):
    return requests.post(
        url,
        data=data,
        json=json,
        timeout=timeout,
    )