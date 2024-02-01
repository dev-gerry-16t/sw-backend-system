import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

SLACK_WEBHOOK_URL = os.getenv('SLACK_WEBHOOK_URL')
SLACK_WEBHOOK_URL_TO_LEAD = os.getenv('SLACK_WEBHOOK_URL_TO_LEAD')


def send_slack_message(message):
    slack_data = {'text': message}
    response = requests.post(
        SLACK_WEBHOOK_URL, data=json.dumps(slack_data),
        headers={'Content-Type': 'application/json'}
    )
    if response.status_code != 200:
        raise ValueError(
            f'Request to slack returned an error {response.status_code}, the response is:\n{response.text}'
        )
    return {"message": "Message sent"}


def send_slack_message_to_lead(message):
    # slack_data = {'text': message,
    #               "attachments": attachments
    #               }
    slack_data = {'text': message
                  }
    response = requests.post(
        SLACK_WEBHOOK_URL_TO_LEAD, data=json.dumps(slack_data),
        headers={'Content-Type': 'application/json'}
    )
    if response.status_code != 200:
        raise ValueError(
            f'Request to slack returned an error {response.status_code}, the response is:\n{response.text}'
        )
    return {"message": "Message sent"}
