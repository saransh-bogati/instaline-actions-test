import responses
import requests
import json
import requests_mock
URL = "http://localhost:5005/webhooks/rest/webhook"

def get_request_data(message: str):
    return json.dumps({
        "sender": "someone",
        "message": message
    })

@responses.activate
def test_hello():
    request_data = get_request_data("hi")
    responses.add(
        responses.POST,
        URL,
        body=request_data
        )
    response = requests.post(URL, data=request_data)
    print(response.text)
    response_json = response.json()
    print(response_json)
    assert response.status_code == 200

    