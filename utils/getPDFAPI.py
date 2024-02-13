import requests
import json
from utils.tokenPDFAPI import generate_jwt_token

def get_pdf(body, template, invoice):
    try:
        token = generate_jwt_token()

        url = f"https://us1.pdfgeneratorapi.com/api/v3/templates/{template}/output?name={invoice}&format=pdf&output=base64"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        # El método utilizado en el código original es 'get', por lo que he mantenido el mismo enfoque aquí.
        response = requests.post(url, headers=headers, data=json.dumps(body))

        response_result = response.json()

        payload = {
            "filename": response_result["meta"]["name"],
            "path": response_result["response"],
        }

        return payload
    except Exception as error:
        raise error
