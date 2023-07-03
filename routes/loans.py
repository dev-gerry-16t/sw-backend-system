from fastapi import APIRouter
from config.db import db
from models.loans import SetNewLoans, ResponseNewLoans
from utils.generateUUID import generate_UUID

loanRouter = APIRouter()

tags_metadata = ["Loans V1"]

collection_loan_information = db["loanInformation"]

@loanRouter.post("/api/v1/loan/createLoans", response_model= ResponseNewLoans ,tags = tags_metadata)
def create_loan_information(loanBody: SetNewLoans):
    loan_info_form = dict(loanBody)

    collection_loan_information.create_index("idSystemUser", unique=True)
    collection_loan_information.create_index("idLoans", unique=True)
    collection_loan_information.insert_one({"idLoans":loan_info_form["idLoans"],"idSystemUser":loan_info_form["idSystemUser"],"loans":[]})

    return {}
