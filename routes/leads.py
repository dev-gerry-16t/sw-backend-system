import requests
import json
import os
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from config.db import db
from utils.generateUUID import generate_UUID

load_dotenv()

HUBSPOT_API_KEY = os.getenv("HUBSPOT_API_KEY")

lead = APIRouter()

tags_metadata = ["Leads V1"]

collection_leads = db["leads"]


@lead.post("/api/v1/lead/create", tags=tags_metadata)
def create_lead(leadBody: dict):
    id_lead = generate_UUID()
    # https://api.hubapi.com/crm/v3/objects/contacts
    first_name = leadBody["firstname"]
    email = leadBody["email"]
    phone = leadBody["phone"]
    message = leadBody["message"]
    try:
        response = requests.post(
            url="https://api.hubapi.com/crm/v3/objects/contacts",
            headers={
                "Authorization": "Bearer " + HUBSPOT_API_KEY,
                "Content-Type": "application/json"
            },
            data=json.dumps({
                "properties": {
                    "email": email,
                    "firstname": first_name,
                    "phone": phone,
                    "message": message
                }
            })
        )

        id_hubspot = response.json()["id"]

        new_lead = {
            "idLead": id_lead,
            "idHubspot": id_hubspot,
            "name": first_name,
            "email": email,
            "phoneNumber": phone,
            "message": message,
            "idStatus": 1,
        }

        collection_leads.create_index("idLead", unique=True)
        collection_leads.insert_one(new_lead)
    except Exception as e:
        raise HTTPException(status_code=500, detail={"dbMessage": str(
            e), "errorMessage": "Hubo un error al intentar guardar el lead"})

    return {"message": "Lead created successfully"}
