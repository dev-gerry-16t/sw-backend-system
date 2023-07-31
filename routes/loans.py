from fastapi import APIRouter
from config.db import db
from models.loans import SetNewLoans, ResponseNewLoans
from utils.generateUUID import generate_UUID
from utils.email import Email

loanRouter = APIRouter()

tags_metadata = ["Loans V1"]

collection_loan = db["loans"]
collection_process = db["process"]
collection_config = db["configs"]
collection_car_info = db["carInformation"]

@loanRouter.post("/api/v1/loan/create", response_model= ResponseNewLoans ,tags = tags_metadata)
def create_loan(loanBody: SetNewLoans):
    request_loan = dict(loanBody)

    email = Email()

    id_loan= generate_UUID()

    new_loan = {
        "idLoan": id_loan,
        "idBankAccount": request_loan["idBankAccount"],
        "requestedAt": request_loan["requestedAt"],
        "concept": request_loan["concept"],
        "amountMonthly":request_loan["amountMonthly"],
        "amountLoan": request_loan["amountLoan"],
        "amountIva": request_loan["amountIva"],
        "amountInterest": request_loan["amountInterest"],
        "amountPayOff": request_loan["amountPayOff"],
        "nextPaymentAt": request_loan["nextPaymentAt"],
        "idStatus":  1 if request_loan["idStatus"] is None else request_loan["idStatus"],
        "approvedAt": None,
        "amountMoratorium": 0,
        "approvedById": None,
        "isLiquidated": False,
        "confirmLiquidatedAt": None,
        "sendPaymentInfoTo":None,
    }

    collection_loan.create_index("idSystemUser", unique=True)
    collection_loan.create_index("idLoans", unique=True)

    existing_loans = collection_loan.find_one({"idSystemUser": request_loan["idSystemUser"]})
    # filter_query = {"idSystemUser":request_loan["idSystemUser"],"process.idProcess": request_loan["idProcess"]}
    
    limit_amount_available= collection_process.find_one({"idSystemUser":request_loan["idSystemUser"]})["amountAvailable"]

    new_values = {"$set": {
        "idStatus": 5 if request_loan["idStatus"] is None else 1,
        "amountAvailable": limit_amount_available - request_loan["amountLoan"],
    }}

    
    if existing_loans:
        collection_loan.update_one(
            {"idSystemUser": request_loan["idSystemUser"]}, 
            {"$addToSet":{"loans":new_loan}}
            )
    else:
        collection_loan.insert_one(
            {"idLoans": request_loan["idLoans"],
            "idSystemUser": request_loan["idSystemUser"],
            "loans":[new_loan]}
            )
        
    collection_process.update_one({"idSystemUser":request_loan["idSystemUser"]} , new_values)

    template_name="SW_REQUESTLOAN_V1"
    email_to = "gerardoaldair@hotmail.com"
    email_from = "Swip <no-reply@info.swip.mx>"
    template_data = {
        "idProcesses": request_loan["idProcesses"],
            }
    email.send_email_template(
        template_name = template_name,
        email_to = email_to,
        email_from = email_from,
        template_data = template_data
    )

    return {"idLoan": id_loan, "idSystemUser": request_loan["idSystemUser"]}

@loanRouter.get("/api/v1/loan/getAll/{idSystemUser}", tags = tags_metadata)
def get_all_loans(idSystemUser: str):

    loans_response= collection_loan.find_one({"idSystemUser": idSystemUser})
    if loans_response is not None:
        loans_response = loans_response["loans"]    
        return {
            "data": loans_response
        }
    else:
        return {
            "data": []
        }

@loanRouter.get("/api/v1/loan/openingPrice/{idProcesses}", tags = tags_metadata)
def get_opening_price(idProcesses: str):

    process_car = collection_process.find_one({"idProcesses": idProcesses}).get("process", None)
    config_info_gps = collection_config.find_one({}).get("gpsMonthly", 0)
    number_of_units = len(process_car)
    total_gps = number_of_units * config_info_gps

    process_car_response = []

    for car in process_car:
        car_info = collection_car_info.find_one({"idCarInformation": car["idCarInformation"]}).get("information", {})
        new_object= {
            "brand": car_info["brand"],
            "model": car_info["model"],
            "year": car_info["year"],
            "numberPlates": car_info["numberPlates"],
            "gpsMonthly": config_info_gps,
        }
        process_car_response.append(new_object)

    return {
        "gpsMonthly": config_info_gps,
        "numberOfUnits": number_of_units,
        "totalGps": total_gps,
        "description": process_car_response
    }