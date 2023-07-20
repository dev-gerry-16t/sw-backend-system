from datetime import datetime
from fastapi import APIRouter
from models.process import SetNewProcess, ResponseNewProcess, ResponseAllProcess, ResponseProcessById, ResponseGetPersonalInfo, ResponseGetCarInfo, ResponseGetBankInfo, RequestUpdateProcessById
from config.db import db
from utils.generateUUID import generate_UUID
from schemas.process import processResponseEntity
from utils.email import Email

process = APIRouter()

tags_metadata = ["Process V1"]

collection_process = db["process"]
collection_profile = db["profiles"]
collection_user = db["customers"]
collection_car_info = db["carInformation"]
collection_bank_info = db["banks"]

@process.post("/api/v1/process/create", response_model= ResponseNewProcess ,tags = tags_metadata)
def create_process(process: SetNewProcess):
    request_process = dict(process)

    timestamp = datetime.now()
    timestamp_formatted = timestamp.strftime("%Y-%m-%d %H:%M:%S")

    id_process= generate_UUID()

    new_process = {
        "idProcess": id_process,
        "createdAt": timestamp_formatted,
        "updatedAt": None,
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
            "idPersonalDocuments": request_process["idPersonalDocuments"],
            "idStatus": 1,
            "amountAvailable": 0,
            "amountApprovedCredit": 0,
            "isApproved": False,
            "approvedById": None,
            "approvedAt": None,
            "createdAt": timestamp_formatted,
            "updatedAt": None,
            "tax": 0.16,
            "interestRate": 0.04,
            "idSystemUser": request_process["idSystemUser"],
            "idLoans": request_process["idLoans"],
            "process":[new_process]}
            )
    
    return processResponseEntity(id_process=id_process, id_processes=  request_process["idProcesses"],id_system_user= request_process["idSystemUser"]);

@process.post("/api/v1/process/infoCreate", tags = tags_metadata)
def info_create_process(request: dict):
    request_info = dict(request)

    email = Email()

    template_name="SW_REQUESTCREDIT_V1"
    email_to = "gerardoaldair@hotmail.com"
    email_from = "Swip <no-reply@info.swip.mx>"
    template_data = {
        "idProcesses": request_info["idProcesses"],
            }
    email.send_email_template(
        template_name = template_name,
        email_to = email_to,
        email_from = email_from,
        template_data = template_data
    )

    return { "message": "Ok" }


@process.get("/api/v1/process/getAll", response_model= ResponseAllProcess ,tags = tags_metadata)
def get_all_process():

    processes_list = []
    processes_db = collection_process.find()

    for proc in processes_db:
        process_main = list(proc["process"])
        name_user = collection_profile.find_one({"idSystemUser": proc["idSystemUser"]})
        process_object = {
            "idProcesses": proc["idProcesses"],
            "idSystemUser": proc["idSystemUser"],
            "name": name_user.get("profileInformation",{}).get("name"),
            "createdAt": proc["createdAt"],
            "idStatus": proc["idStatus"],
            "processes": len(process_main),
            "amountApprovedCredit": proc["amountApprovedCredit"],
            "approvedAt": proc["approvedAt"],
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
    process_main = dict(processes_db)

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

@process.get("/api/v1/process/getCarInfo/{idSystemUser}", response_model= ResponseGetCarInfo ,tags = tags_metadata)
def get_personal_info(idSystemUser: str):

    car_info = dict(collection_car_info.find_one({"idSystemUser": idSystemUser},{"_id":0,"idCarInformation":0,"idSystemUser":0}).get("information",{}))
 

    return car_info

@process.get("/api/v1/process/getBankInfo/{idSystemUser}", response_model= ResponseGetBankInfo ,tags = tags_metadata)
def get_personal_info(idSystemUser: str):

    bank_info = dict(collection_bank_info.find_one({"idSystemUser": idSystemUser},{"_id":0,"idBankAccounts":0,"idSystemUser":0}).get("bankInformation",[])[0])
 

    return bank_info

@process.put("/api/v1/process/updateById/{idProcess}",tags = tags_metadata)
def update_process_by_id(idProcess: str, process: RequestUpdateProcessById):
    request_process = dict(process)
    id_system_user = request_process["idSystemUser"]
    
    email = Email()

    filter_query = {"idSystemUser":id_system_user,"process.idProcess": idProcess}

    new_values = {"$set": {}}

    for key, value in request_process.items():
        if key not in ["idProcess", "idSystemUser", "amountApprovedCreditFormatted"]:
            field = f"process.$.{key.replace('_', '')}"
            new_values["$set"][field] = value

    collection_process.find_one_and_update(filter_query, new_values)
    user_info = dict(collection_user.find_one({"idSystemUser": id_system_user},{"email":1}))
    profile_name = collection_profile.find_one({"idSystemUser": id_system_user}).get("profileInformation", {}).get("name")

    template_name=""
    email_to = "gerardoaldair@hotmail.com"
    email_from = "Swip <no-reply@info.swip.mx>"
    template_data = {}

    if request_process["idStatus"] == 2:
        template_name="SW_APPROVEDCREDIT_V2"
        template_data = {
            "user": profile_name,
            "amountApprovedCredit":f'{request_process["amountApprovedCreditFormatted"]} MXN',
             }
        email.send_email_template(
            template_name = template_name,
            email_to = email_to,
            email_from = email_from,
            template_data = template_data
        )
    elif request_process["idStatus"] == 3:
        template_name="SW_REJECTEDCREDIT_V1"
        template_data = {
            "user": profile_name,
             }
        email.send_email_template(
            template_name = template_name,
            email_to = email_to,
            email_from = email_from,
            template_data = template_data
        )


    return {
        "message": "Process updated successfully"
    }

@process.put("/api/v1/process/updateByIdProcesses/{idProcesses}",tags = tags_metadata)
def update_process_by_id(idProcesses: str, process: RequestUpdateProcessById):
    request_process = dict(process)
    id_system_user = request_process["idSystemUser"]
    
    email = Email()

    filter_query = {"idSystemUser":id_system_user,"process.idProcess": idProcesses}

    new_values = {"$set": {}}

    for key, value in request_process.items():
        if key not in ["idProcess", "idSystemUser", "amountApprovedCreditFormatted"]:
            field = f"process.$.{key.replace('_', '')}"
            new_values["$set"][field] = value

    collection_process.find_one_and_update(filter_query, new_values)
    user_info = dict(collection_user.find_one({"idSystemUser": id_system_user},{"email":1}))
    profile_name = collection_profile.find_one({"idSystemUser": id_system_user}).get("profileInformation", {}).get("name")

    template_name=""
    email_to = "gerardoaldair@hotmail.com"
    email_from = "Swip <no-reply@info.swip.mx>"
    template_data = {}

    if request_process["idStatus"] == 2:
        template_name="SW_APPROVEDCREDIT_V2"
        template_data = {
            "user": profile_name,
            "amountApprovedCredit":f'{request_process["amountApprovedCreditFormatted"]} MXN',
             }
        email.send_email_template(
            template_name = template_name,
            email_to = email_to,
            email_from = email_from,
            template_data = template_data
        )
    elif request_process["idStatus"] == 3:
        template_name="SW_REJECTEDCREDIT_V1"
        template_data = {
            "user": profile_name,
             }
        email.send_email_template(
            template_name = template_name,
            email_to = email_to,
            email_from = email_from,
            template_data = template_data
        )


    return {
        "message": "Process updated successfully"
    }






