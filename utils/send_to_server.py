import requests


def send_to_server(url, data):
    try:
        response = requests.post(url, json={"data": data})
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print("Error: ", e)