from fastapi import APIRouter
from config.db import db
from models.loans import SetNewLoans, ResponseNewLoans
from utils.generateUUID import generate_UUID
from utils.email import Email

loanRouter = APIRouter()

tags_metadata = ["Loans V1"]

collection_loan = db["loans"]
collection_process = db["process"]

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
        "idStatus": 1,
        "approvedAt": None,
        "tax": 0.16,
        "interestRate": 0.04,
        "amountMoratorium": 0,
        "approvedById": None,
        "isLiquidated": False,
        "confirmLiquidatedAt": None,
        "sendPaymentInfoTo":None,
    }

    collection_loan.create_index("idSystemUser", unique=True)
    collection_loan.create_index("idLoans", unique=True)

    existing_loans = collection_loan.find_one({"idSystemUser": request_loan["idSystemUser"]})
    filter_query = {"idSystemUser":request_loan["idSystemUser"],"process.idProcess": request_loan["idProcess"]}
    
    limit_amount_available= collection_process.find_one(filter_query)["process"][0]["amountAvailable"]

    new_values = {"$set": {
        "process.$.idStatus": 1,
        "process.$.amountAvailable": limit_amount_available - request_loan["amountLoan"],
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
        
    collection_process.find_one_and_update(filter_query , new_values)

    template_name="SW_REQUESTLOAN_V1"
    email_to = "gerardocto@swip.mx"
    email_from = "no-reply@info.swip.mx"
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

    loans_response= collection_loan.find_one({"idSystemUser": idSystemUser})["loans"]
    
    return {
        "data": loans_response
    }