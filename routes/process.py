from datetime import datetime
from fastapi import APIRouter
from models.process import SetNewProcess, ResponseNewProcess, ResponseAllProcess, ResponseProcessById, ResponseGetPersonalInfo
from config.db import db
from utils.generateUUID import generate_UUID
from schemas.process import processResponseEntity

process = APIRouter()

tags_metadata = ["Process V1"]

collection_process = db["process"]
collection_profile = db["profile"]
collection_user = db["user"]

@process.post("/api/v1/process/create", response_model= ResponseNewProcess ,tags = tags_metadata)
def create_process(process: SetNewProcess):
    request_process = dict(process)

    timestamp = datetime.now()
    timestamp_formatted = timestamp.strftime("%Y-%m-%d %H:%M:%S")

    id_process= generate_UUID()

    new_process = {
        "idProcess": id_process,
        "idStatus": 1,
        "amountAvailable": 0,
        "amountApprovedCredit": 0,
        "isApproved": False,
        "approvedById": None,
        "approvedAt": None,
        "createdAt": timestamp_formatted,
        "updatedAt": None,
        "idLoans": request_process["idLoans"],
        "idCarDocuments": request_process["idCarDocuments"],
        "idCarInformation": request_process["idCarInformation"],
    }

    collection_process.create_index("idSystemUser", unique=True)

    existing_process = collection_process.find_one({"idSystemUser": request_process["idSystemUser"]})

    if existing_process:
        collection_process.update_one(
            {"idSystemUser": request_process["idSystemUser"]}, 
            {"$addToSet":{"process":new_process}}
            )
    else:
        collection_process.insert_one(
            {"idProcesses": request_process["idProcesses"],
            "idSystemUser": request_process["idSystemUser"],
            "process":[new_process]}
            )
    
    return processResponseEntity(id_process=id_process, id_processes=  request_process["idProcesses"],id_system_user= request_process["idSystemUser"]);

@process.get("/api/v1/process/getAll", response_model= ResponseAllProcess ,tags = tags_metadata)
def get_all_process():

    processes_list = []
    processes_db = collection_process.find()

    for proc in processes_db:
        process_main = dict(proc["process"][0])
        name_user = collection_profile.find_one({"idSystemUser": proc["idSystemUser"]})
        process_object = {
            "idProcesses": proc["idProcesses"],
            "idProcess": process_main["idProcess"],
            "idSystemUser": proc["idSystemUser"],
            "name": name_user.get("profileInformation",{}).get("name"),
            "createdAt": process_main["createdAt"],
            "idStatus": process_main["idStatus"],
            "processes": 1,
            "amountApprovedCredit": process_main["amountApprovedCredit"],
            "approvedAt": process_main["approvedAt"],
            "loansRequested": 0,
        }
        processes_list.append(process_object)

    return {
        "data": processes_list
    }

@process.get("/api/v1/process/getById/{id}", response_model= ResponseProcessById ,tags = tags_metadata)
def get_process_by_id(id: str):
    processes_db = collection_process.find_one({"idProcesses": id})
    id_system_user = processes_db.get("idSystemUser",None)
    process_main = dict(processes_db.get("process",[])[0])

    object_response = {
        "idProcesses": id,
        "idSystemUser": id_system_user,
        **process_main
    }

    return object_response

@process.get("/api/v1/process/getPersonalInfo/{idSystemUser}", response_model= ResponseGetPersonalInfo ,tags = tags_metadata)
def get_personal_info(idSystemUser: str):

    user_info = dict(collection_user.find_one({"idSystemUser": idSystemUser},{"email":1,"phoneNumber":1}))
    profile_info = dict(collection_profile.find_one({"idSystemUser": idSystemUser},{"_id":0,"idProfile":0,"idSystemUser":0}))
    address_info=profile_info["addressInformation"]
    deserealize_profile_info = profile_info["profileInformation"]

    return {
        **user_info,
        **deserealize_profile_info,
        "addressInformation":address_info,
    }






