import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

url_slack = os.getenv('SLACK_WEBHOOK_URL')

def send_slack_message(message):
    slack_data = {'text': message}
    response = requests.post(
        url_slack, data=json.dumps(slack_data),
        headers={'Content-Type': 'application/json'}
    )
    if response.status_code != 200:
        raise ValueError(
            f'Request to slack returned an error {response.status_code}, the response is:\n{response.text}'
        )
    return {"message": "Message sent"}