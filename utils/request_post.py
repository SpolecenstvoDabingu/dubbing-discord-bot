import requests

def request_post(url, data=None, timeout=10):
    return requests.post(
        url,
        data=data,
        timeout=timeout,
    )