import json

from datetime import datetime
from fastapi import APIRouter, UploadFile, UploadFile, File, Form
from models.personalDocument import ResponseModelScreen
from utils.generateUUID import generate_UUID
from config.db import db

document = APIRouter()

tags_metadata = ["Personal Document V1"]

collection = db["dynamicDocument"]
collection_screen = db["screenDocument"]
collection_type_document = db["typeDocument"]
collection_personal_document = db["personalDocument"]
collection_repository_document = db["repositoryDocument"]

@document.post("/api/v1/document/upload",tags = tags_metadata)
async def upload_file(file: UploadFile = File(...),
                       data: str = Form(...)):
    
    id_document=generate_UUID()
    data_json = json.loads(data)

    new_document = {
        "idDocument": id_document,
        "getInfoAI":""
    }

    collection_personal_document.create_index("idPersonalDocuments", unique=True)
    collection_personal_document.create_index("idSystemUser", unique=True)
    collection_repository_document.create_index("idDocument", unique=True)

    existing_document = collection_personal_document.find_one({"idSystemUser": data_json["idSystemUser"]})
    timestamp = datetime.now()
    timestamp_formatted = timestamp.strftime("%Y-%m-%d %H:%M:%S")
    
    collection_repository_document.insert_one({
            "idDocument": id_document, 
            "documentName": data_json["name"],
            "bucketSource": data_json["bucketSource"],
            "idDocumentType": data_json["idDocumentType"],
            "extension": data_json["type"].split("/")[-1],
            "mimetype": data_json["type"],
            "dateUpload": timestamp_formatted,
            "size": data_json["size"],             
            })


    if existing_document:
        collection_personal_document.update_one(
            {"idSystemUser": data_json["idSystemUser"]}, 
            {"$addToSet":{"personalDocuments":new_document}}
            )
    else:
        collection_personal_document.insert_one(
            {"idPersonalDocuments": data_json["idPersonalDocuments"],
            "idSystemUser": data_json["idSystemUser"],
            "personalDocuments":[new_document]}
            )
    


    contents = await file.read()

    return "OK"

@document.get("/api/v1/document/getFlowScreenDocument/{idUserType}", response_model = ResponseModelScreen,tags = tags_metadata)
async def get_flow_screen_document(idUserType: str):
    int_id_user= int(idUserType)
    flows_screen=[]
    if int_id_user == 0:
        document = list(collection.find())
        for doc in document:
            document_type =  collection_type_document.find_one({"idDocumentType": doc["idDocumentType"]}, {"_id": 0})    
            document_screen =  collection_screen.find_one({"idScreen": doc["idScreen"]}, {"_id": 0})
            flow_screen ={"isLast":doc["isLast"],**document_screen, **document_type}
            flows_screen.append(flow_screen)

    return {"screens" : flows_screen}
    
        


