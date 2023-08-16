import json

from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from models.personalDocument import ResponseModelScreen
from utils.generateUUID import generate_UUID
from config.db import db
from utils.objectS3 import ObjectS3
from utils.formatDate import FormatDate

document = APIRouter()

tags_metadata = ["Personal Document V1"]

collection = db["dynamicDocuments"]
collection_moral = db["dynamicMoralDocuments"]
collection_car = db["dynamicCarDocuments"]
collection_car_moral = db["dynamicCarMoralDocuments"]

collection_personal_document = db["personalDocuments"]
collection_car_document = db["carDocuments"]

collection_type_document = db["typeDocuments"]
collection_repository_document = db["repositoryDocuments"]

@document.post("/api/v1/document/upload",tags = tags_metadata)
async def upload_file(file: UploadFile = File(...),
                       data: str = Form(...)):
    s3_object = ObjectS3()
    
    id_document=generate_UUID()
    data_json = json.loads(data)
    id_flow_document = data_json["idFlowDocumentType"]
    format_iso= FormatDate()

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
 


    collection_repository_document.create_index("idDocument", unique=True)
    collection_repository_document.insert_one({
            "idDocument": id_document, 
            "isActive": True,
            "documentName": data_json["name"],
            "bucketSource": data_json["bucketSource"],
            "idDocumentType": data_json["idDocumentType"],
            "extension": data_json["type"].split("/")[-1],
            "mimetype": data_json["type"],
            "dateUpload": format_iso.timezone_cdmx(),
            "size": data_json["size"],             
            })
    

    if id_flow_document == 0:
        collection_personal_document.create_index("idSystemUser", unique=True)

        existing_document = collection_personal_document.find_one({"idSystemUser": data_json["idSystemUser"]})

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
            
    elif id_flow_document == 1:
        collection_car_document.create_index("idCarDocuments", unique=True)

        existing_document = collection_car_document.find_one({"idCarDocuments": data_json["idCarDocuments"]})

        if existing_document:
            collection_car_document.update_one(
                {"idCarDocuments": data_json["idCarDocuments"]}, 
                {"$addToSet":{"carDocuments":new_document}}
                )
        else:
            collection_car_document.insert_one(
                {"idCarDocuments": data_json["idCarDocuments"],
                "idSystemUser": data_json["idSystemUser"],
                "carDocuments":[new_document]}
                )



    return "OK"

@document.post("/api/v1/document/reUpload",tags = tags_metadata)
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

    collection_repository_document.find_one_and_update({"idDocument": id_document}, {"$set": {"dateUpload": format_iso.timezone_cdmx(), "size": data_json["size"],**meta_data}})

    return "OK"

@document.post("/api/v1/document/getFlowScreenDocument", response_model = ResponseModelScreen,tags = tags_metadata)
async def post_flow_screen_document(requestFlow: dict):
    int_id_user= requestFlow["idUserType"]
    flow_document_type= requestFlow["idFlowDocumentType"]

    flows_screen=[]
    if flow_document_type == 0:
        if int_id_user == 0:
            document = list(collection.find().sort("index",1))
        elif int_id_user == 1:
            document = list(collection_moral.find().sort("index",1))
        for doc in document:
            document_type =  collection_type_document.find_one({"idDocumentType": doc["idDocumentType"]}, {"_id": 0})

            flow_screen ={**document_type, "idScreen": doc["idScreen"], "index": doc["index"]}
            flows_screen.append(flow_screen)
    elif flow_document_type == 1:
        if int_id_user == 0:
            document = list(collection_car.find().sort("index",1))
        elif int_id_user == 1:
            document = list(collection_car_moral.find().sort("index",1))
        for doc in document:
            document_type =  collection_type_document.find_one({"idDocumentType": doc["idDocumentType"]}, {"_id": 0})

            flow_screen ={**document_type, "idScreen": doc["idScreen"], "index": doc["index"]}
            flows_screen.append(flow_screen)
        

    return {"screens" : flows_screen}

@document.put("/api/v1/document/updateFlowScreenDocument", tags = tags_metadata)
async def put_flow_screen_document(requestFlow: dict):
    int_id_user= requestFlow["idUserType"]
    flow_document_type= requestFlow["idFlowDocumentType"]
    new_flow_documents= requestFlow["flowDocuments"]

    for doc in new_flow_documents:
        if flow_document_type == 0:
            if int_id_user == 0:
                collection.update_one(
                    {"idScreen": doc["idScreen"]}, 
                    {"$set":{"index": doc["index"]}}
                    )
            elif int_id_user == 1:
                collection_moral.update_one(
                    {"idScreen": doc["idScreen"]}, 
                    {"$set":{"index": doc["index"]}}
                    )
        elif flow_document_type == 1:
            if int_id_user == 0:
                collection_car.update_one(
                    {"idScreen": doc["idScreen"]}, 
                    {"$set":{"index": doc["index"]}}
                    )
            elif int_id_user == 1:
                collection_car_moral.update_one(
                    {"idScreen": doc["idScreen"]}, 
                    {"$set":{"index": doc["index"]}}
                    )
                
    return {"message": "Ok"}

@document.get("/api/v1/document/getDocument/{bucketSource}/{idDocument}",tags = tags_metadata)
def get_document(bucketSource: str, idDocument: str):
    s3_object = ObjectS3()
    document, metadata =  s3_object.get_object(bucket_name = bucketSource,file_name = idDocument)
    return StreamingResponse(iter([document]), media_type=metadata.get("mimetype", "image/jpeg"))

@document.get("/api/v1/document/getPersonalDocumentsById/{idPersonalDocuments}",tags = tags_metadata)
def get_personal_by_id(idPersonalDocuments: str):

    response_db_documents = collection_personal_document.find_one({"idPersonalDocuments": idPersonalDocuments}).get("personalDocuments",[])
    response_list_documents = list(response_db_documents)

    documents = []

    for document in response_list_documents:
        document_info = collection_repository_document.find_one({"idDocument": document["idDocument"], "isActive": True}, {"_id": 0})
        if document_info is not None:
            document_type =  collection_type_document.find_one({"idDocumentType": document_info["idDocumentType"]}, {"_id": 0})
            document_info["url"] = f"/api/v1/document/getDocument/{document_info['bucketSource']}/{document_info['idDocument']}"
            document_info["name"] = document_type["name"]
            documents.append(document_info)

    return {"data": documents}

@document.get("/api/v1/document/getCarDocumentsById/{idCarDocuments}",tags = tags_metadata)
def get_car_by_id(idCarDocuments: str):

    response_documents = collection_car_document.find_one({"idCarDocuments": idCarDocuments}).get("carDocuments",[])
    response_list_documents = list(response_documents)

    documents = []

    for document in response_list_documents:
        document_info = collection_repository_document.find_one({"idDocument": document["idDocument"], "isActive": True}, {"_id": 0})
        if document_info is not None:
            document_type =  collection_type_document.find_one({"idDocumentType": document_info["idDocumentType"]}, {"_id": 0})        
            document_info["url"] = f"/api/v1/document/getDocument/{document_info['bucketSource']}/{document_info['idDocument']}"
            document_info["name"] = document_type["name"]
            documents.append(document_info)

    return {"data": documents}

@document.put("/api/v1/document/deactivateDocument/{idDocument}",tags = tags_metadata)
def deactivate_document(idDocument: str):
    collection_repository_document.update_one({"idDocument": idDocument}, {"$set":{"isActive": False}})
    return {"message": "OK"}

    
        


