import json
from fastapi import APIRouter, UploadFile, File, Form
from utils.generateUUID import generate_UUID
from config.db import db
from utils.objectS3 import ObjectS3
from datetime import datetime
from utils.formatDate import FormatDate
from utils.customDictionary import CustomDictionary

adminDocument = APIRouter()

tags_metadata = ["Admin Document V1"]

collection_repository_admin_document = db["repositoryAdminDocuments"]
collection_admin_document = db["adminDocuments"]
collection_document_type = db["typeAdminDocuments"]

@adminDocument.post("/api/v1/adminDocument/upload",tags = tags_metadata)
async def upload_file(file: UploadFile = File(...),
                       data: str = Form(...)):
    s3_object = ObjectS3()
    format_iso= FormatDate()
    
    id_document=generate_UUID()
    data_json = json.loads(data)

    new_document = {
        "idDocument": id_document,
        "getInfoAI":""
    }

    meta_data = {
            "documentName": data_json["name"],
            "idDocumentType": data_json["idDocumentType"],
            "extension": data_json["type"].split("/")[-1],
            "mimetype": data_json["type"],
    }

    contents = await file.read()

    
    s3_object.upload_file(
        file_name = id_document,
        bucket_name = data_json["bucketSource"],
        file_content = contents,
        meta_data = meta_data
    )
 


    collection_repository_admin_document.create_index("idDocument", unique=True)
    collection_repository_admin_document.insert_one({
            **meta_data,
            "idDocument": id_document, 
            "isActive": True,
            "customName": data_json["customName"],
            "bucketSource": data_json["bucketSource"],
            "dateUpload": format_iso.timezone_cdmx(),
            "size": data_json["size"],             
            })
    

    
    collection_admin_document.create_index("idSystemUser", unique=True)

    existing_document = collection_admin_document.find_one({"idSystemUser": data_json["idSystemUser"]})

    if existing_document:
        collection_admin_document.update_one(
            {"idSystemUser": data_json["idSystemUser"]}, 
            {"$addToSet":{"adminDocuments":new_document}}
            )
    else:
        collection_admin_document.insert_one(
            {"idSystemUser": data_json["idSystemUser"],
             "idProcesses": data_json["idProcesses"],
            "adminDocuments":[new_document]}
                )

    return "OK"

@adminDocument.post("/api/v1/adminDocument/reUpload",tags = tags_metadata)
async def re_upload_file(file: UploadFile = File(...),
                       data: str = Form(...)):
    s3_object = ObjectS3()
    
    data_json = json.loads(data)
    id_document=data_json["idDocument"]
    format_iso= FormatDate()

    meta_data = {
            "documentName": data_json["documentName"],
            "idDocumentType": data_json["idDocumentType"],
            "extension": data_json["type"].split("/")[-1],
            "mimetype": data_json["type"],
    }

    contents = await file.read()

    
    s3_object.upload_file(
        file_name = id_document,
        bucket_name = data_json["bucketSource"],
        file_content = contents,
        meta_data = meta_data
    )

    collection_repository_admin_document.find_one_and_update({"idDocument": id_document}, {"$set": {"dateUpload": format_iso.timezone_cdmx(), "size": data_json["size"],**meta_data}})

    return "OK"

@adminDocument.get("/api/v1/adminDocument/catalog/getAllDocumentTypes", tags = tags_metadata)
def get_all_document_types():
    document_types = list(collection_document_type.find({},{"_id":0, "label":0}))
    return {
        "data": document_types
    }

@adminDocument.get("/api/v1/adminDocument/getAdminDocumentsById/{idSystemUser}",tags = tags_metadata)
def get_admin_document_by_id(idSystemUser: str):

    custom_dictionary = CustomDictionary(collection_admin_document.find_one({"idSystemUser": idSystemUser}))
    response_db_documents = custom_dictionary.get("adminDocuments",[])
    response_list_documents = list(response_db_documents)

    documents = []

    for document in response_list_documents:
        document_info = collection_repository_admin_document.find_one({"idDocument": document["idDocument"], "isActive": True}, {"_id": 0})
        if document_info is not None:
            document_type =  collection_document_type.find_one({"idDocumentType": document_info["idDocumentType"]}, {"_id": 0})
            document_info["url"] = f"/api/v1/document/getDocument/{document_info['bucketSource']}/{document_info['idDocument']}"
            document_info["name"] = document_type["name"]
            documents.append(document_info)

    return {"data": documents}

@adminDocument.put("/api/v1/adminDocument/deactivateDocument/{idDocument}",tags = tags_metadata)
def deactivate_document(idDocument: str):
    collection_repository_admin_document.update_one({"idDocument": idDocument}, {"$set":{"isActive": False}})
    return {"message": "OK"}