import locale
from datetime import datetime
from fastapi import APIRouter
from models.process import SetNewProcess, ResponseNewProcess, ResponseAllProcess, ResponseProcessById, ResponseGetPersonalInfo, ResponseGetCarInfo, ResponseGetBankInfo, RequestUpdateProcessById
from config.db import db
from utils.generateUUID import generate_UUID
from schemas.process import processResponseEntity
from utils.email import Email
from utils.selectTemplateEmail import select_template_email
from utils.formatDate import FormatDate
process = APIRouter()

tags_metadata = ["Process V1"]

collection_process = db["process"]
collection_config = db["configs"]
collection_profile = db["profiles"]
collection_user = db["customers"]
collection_car_info = db["carInformation"]
collection_bank_info = db["banks"]
collection_car_docs = db["carDocuments"]
collection_loan = db["loans"]

collection_type_document = db["typeDocuments"]
collection_repository_document = db["repositoryDocuments"]


@process.post("/api/v1/process/create", response_model=ResponseNewProcess, tags=tags_metadata)
def create_process(process: SetNewProcess):
    request_process = dict(process)

    format_iso = FormatDate()

    id_process = generate_UUID()

    new_process = {
        "idProcess": id_process,
        "createdAt": format_iso.timezone_cdmx(),
        "updatedAt": None,
        "idCarDocuments": request_process["idCarDocuments"],
        "idCarInformation": request_process["idCarInformation"],
    }

    collection_process.create_index("idSystemUser", unique=True)

    existing_process = collection_process.find_one(
        {"idSystemUser": request_process["idSystemUser"]})

    if existing_process:
        collection_process.update_one(
            {"idSystemUser": request_process["idSystemUser"]},
            {"$addToSet": {"process": new_process}}
        )
    else:
        configs_rule = collection_config.find_one({})
        config_level = configs_rule["configLevel"]
        customer_level = collection_user.find_one({"idSystemUser": request_process["idSystemUser"]}, {"level": 1})
        interest_by_level = 0
        for level in config_level:
            if customer_level["level"] == level["level"]:
                interest_by_level = level["interest"]
                break

        collection_process.insert_one(
            {"idProcesses": request_process["idProcesses"],
             "idPersonalDocuments": request_process["idPersonalDocuments"],
             "idStatus": 1,
             "amountAvailable": 0,
             "amountApprovedCredit": 0,
             "isApproved": False,
             "approvedById": None,
             "approvedAt": None,
             "createdAt": format_iso.timezone_cdmx(),
             "updatedAt": None,
             "tax":  configs_rule["tax"] if configs_rule is not None else 0.16,
             "interestRate": interest_by_level if interest_by_level is not 0 else 0.067,
             "idSystemUser": request_process["idSystemUser"],
             "idLoans": request_process["idLoans"],
             "appointmentDate": None,
             "process": [new_process]}
        )

    return processResponseEntity(id_process=id_process, id_processes=request_process["idProcesses"], id_system_user=request_process["idSystemUser"])


@process.post("/api/v1/process/infoCreate", tags=tags_metadata)
def info_create_process(request: dict):
    request_info = dict(request)

    select_template_email(
        id_template=1,
        id_processes=request_info["idProcesses"],
    )

    return {"message": "Ok"}


@process.get("/api/v1/process/getAll", response_model=ResponseAllProcess, tags=tags_metadata)
def get_all_process():

    processes_list = []
    processes_db = collection_process.find()
    for proc in processes_db:
        process_main = list(proc["process"])
        name_user = collection_profile.find_one(
            {"idSystemUser": proc["idSystemUser"]})
        process_object = {
            "idProcesses": proc["idProcesses"],
            "idSystemUser": proc["idSystemUser"],
            "name": name_user.get("profileInformation", {}).get("name"),
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


@process.get("/api/v1/process/getById/{id}", response_model=ResponseProcessById, tags=tags_metadata)
def get_process_by_id(id: str):
    processes_db = collection_process.find_one({"idProcesses": id})
    process = processes_db.get("process", None)
    id_system_user = processes_db.get("idSystemUser", None)
    loan_find_one = collection_loan.find_one({"idSystemUser": id_system_user})
    loans_user = [] if loan_find_one is None else loan_find_one.get(
        "loans", [])

    process_list = []

    calc_amount_credit = 0
    for proc in process:
        car_info = collection_car_info.find_one({"idCarInformation": proc["idCarInformation"]}, {
                                                "_id": 0, "idCarInformation": 0, "idSystemUser": 0})["information"]
        car_docs = collection_car_docs.find_one({"idCarDocuments": proc["idCarDocuments"]}, {
                                                "_id": 0, "idCarDocuments": 0, "idSystemUser": 0})["carDocuments"]
        calc_amount_credit += car_info["amountPrice"]
        documents = []
        for document in car_docs:
            document_info = collection_repository_document.find_one(
                {"idDocument": document["idDocument"], "isActive": True}, {"_id": 0})
            if document_info is not None:
                document_type = collection_type_document.find_one(
                    {"idDocumentType": document_info["idDocumentType"]}, {"_id": 0})
                document_info["url"] = f"/api/v1/document/getDocument/{document_info['bucketSource']}/{document_info['idDocument']}"
                document_info["name"] = document_type["name"]
                documents.append(document_info)

        new_object = {
            **proc,
            **car_info,
            "documents": documents,
        }

        process_list.append(new_object)

    calc_amount_loans = 0
    for loan in loans_user:
        calc_amount_loans += loan["amountLoan"]

    if processes_db["idStatus"] == 1 or processes_db["idStatus"] == 2:
        collection_process.update_one({"idProcesses": id}, {"$set": {
                                      "amountAvailable": calc_amount_credit - calc_amount_loans, "amountApprovedCredit": calc_amount_credit}})
        processes_db = collection_process.find_one({"idProcesses": id})

    process_main = dict(processes_db)

    object_response = {
        "idProcesses": id,
        "idSystemUser": id_system_user,
        **process_main,
        "process": process_list,
    }

    return object_response


@process.get("/api/v1/process/getPersonalInfo/{idSystemUser}", response_model=ResponseGetPersonalInfo, tags=tags_metadata)
def get_personal_info(idSystemUser: str):

    user_info = dict(collection_user.find_one(
        {"idSystemUser": idSystemUser}, {"email": 1, "phoneNumber": 1, "level": 1}))
    profile_info = dict(collection_profile.find_one(
        {"idSystemUser": idSystemUser}, {"_id": 0, "idProfile": 0, "idSystemUser": 0}))
    address_info = profile_info["addressInformation"]
    deserealize_profile_info = profile_info["profileInformation"]

    return {
        **user_info,
        **deserealize_profile_info,
        "addressInformation": address_info,
    }


@process.get("/api/v1/process/getCarInfo/{idSystemUser}", response_model=ResponseGetCarInfo, tags=tags_metadata)
def get_personal_info(idSystemUser: str):

    car_info = dict(collection_car_info.find_one({"idSystemUser": idSystemUser}, {
                    "_id": 0, "idCarInformation": 0, "idSystemUser": 0}).get("information", {}))

    return car_info


@process.get("/api/v1/process/getBankInfo/{idSystemUser}", response_model=ResponseGetBankInfo, tags=tags_metadata)
def get_personal_info(idSystemUser: str):

    bank_info = dict(collection_bank_info.find_one({"idSystemUser": idSystemUser}, {
                     "_id": 0, "idBankAccounts": 0, "idSystemUser": 0}).get("bankInformation", [])[0])

    return bank_info


@process.put("/api/v1/process/updateById/{idProcess}", tags=tags_metadata)
def update_process_by_id(idProcess: str, process: dict):
    request_process = dict(process)
    id_processes = request_process["idProcesses"]
    id_car_information = request_process["idCarInformation"]
    format_iso = FormatDate()

    update_processes = format_iso.timezone_cdmx()

    collection_process.find_one_and_update({"idProcesses": id_processes, "process.idProcess": idProcess}, {
                                           "$set": {"process.$.updatedAt": update_processes}})

    new_values = {"$set": {}}
    for key, value in request_process.items():
        if key not in ["idProcess", "idSystemUser", "amountApprovedCreditFormatted", "updatedAt", "idCarInformation", "idProcesses", "offset"]:
            field = f"information.{key.replace('_', '')}"
            new_values["$set"][field] = value

    collection_car_info.update_one(
        {"idCarInformation": id_car_information}, new_values)

    return {
        "message": "Process updated successfully"
    }


@process.put("/api/v1/process/updateByIdProcesses/{idProcesses}", tags=tags_metadata)
def update_process_by_id(idProcesses: str, process: dict):
    request_process = dict(process)
    format_iso = FormatDate()
    id_system_user = request_process["idSystemUser"]
    id_status_process = request_process.get("idStatus", None)
    id_template_email = request_process.get("idTemplateEmail", None)

    filter_query = {"idProcesses": idProcesses}

    new_values = {"$set": {}}

    for key, value in request_process.items():
        if key not in ["idProcess", "idSystemUser", "amountApprovedCreditFormatted", "idTemplateEmail", "offset"]:
            field = key.replace('_', '')
            if key in ["approvedAt", "updatedAt"]:
                new_values["$set"][field] = format_iso.timezone_cdmx()
            else:
                new_values["$set"][field] = value

    collection_process.update_one(filter_query, new_values)
    profile_name = collection_profile.find_one(
        {"idSystemUser": id_system_user}).get("profileInformation", {}).get("name")

    if id_template_email is not None:
        if id_template_email == 1:
            select_template_email(
                id_template=id_template_email,
                id_processes=idProcesses,
            )
        if id_template_email == 2:
            user_info = dict(collection_user.find_one(
                {"idSystemUser": id_system_user}, {"email": 1}))
            email_to = user_info["email"]
            select_template_email(
                id_template=id_template_email,
                email_to=email_to,
                user=profile_name,
                amount_approved=f'{request_process["amountApprovedCreditFormatted"]} MXN'
            )
        if id_template_email == 3:
            user_info = dict(collection_user.find_one(
                {"idSystemUser": id_system_user}, {"email": 1}))
            email_to = user_info["email"]
            select_template_email(
                id_template=id_template_email,
                email_to=email_to,
                user=profile_name
            )
        if id_template_email == 4:
            user_info = dict(collection_user.find_one(
                {"idSystemUser": id_system_user}, {"email": 1}))
            email_to = user_info["email"]
            select_template_email(
                id_template=id_template_email,
                id_processes=idProcesses,
            )
        if id_template_email == 7:
            user_info = dict(collection_user.find_one(
                {"idSystemUser": id_system_user}, {"email": 1}))
            email_to = user_info["email"]
            select_template_email(
                id_template=id_template_email,
                id_system_user=id_system_user,
                email_to=email_to,
                amount_approved=f'{request_process["amountApprovedCreditFormatted"]} MXN',
                user=profile_name,
            )
        if id_template_email == 8 or id_template_email == 9:
            locale.setlocale(locale.LC_TIME, 'es_MX.utf8')
            user_info = dict(collection_user.find_one(
                {"idSystemUser": id_system_user}, {"email": 1}))
            email_to = user_info["email"]
            date = request_process["appointmentDate"]
            date_object = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S%z')
            day = date_object.day
            month = date_object.strftime("%B")
            year = date_object.year
            hour = date_object.strftime("%I:%M")
            am_pm = "AM" if date_object.hour < 12 else "PM"
            format_date = f'{day} de {month} del {year} a las {hour} {am_pm}'
            select_template_email(
                id_template=8,
                appointment_date=format_date,
                id_processes=idProcesses,
                user=profile_name,
            )
            select_template_email(
                id_template=9,
                email_to=email_to,
                appointment_date=format_date,
                user=profile_name,
            )

    return {
        "message": "Process updated successfully"
    }
