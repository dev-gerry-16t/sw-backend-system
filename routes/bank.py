from fastapi import APIRouter
from models.bank import SetNewBank, ResponseNewBank
from utils.generateUUID import generate_UUID
from config.db import db
from schemas.bank import bankResponseEntity

bankRouter = APIRouter()

tags_metadata = ["Bank V1"]

collection_bank_information = db["bank"]

@bankRouter.post("/api/v1/bank/create", response_model= ResponseNewBank ,tags = tags_metadata)
def create_bank_information(bankBody: SetNewBank):
    bank_info_form = dict(bankBody)
    id_bank_account = generate_UUID()

    bank_information = {
        "idBankAccount": id_bank_account,
        "beneficiary": bank_info_form["beneficiary"],
        "numberAccount": bank_info_form["numberAccount"],
        "clabe": bank_info_form["clabe"],
        "bank": bank_info_form["bank"],
    }

    collection_bank_information.create_index("idSystemUser", unique=True)
    collection_bank_information.insert_one({
            "idBankAccounts": bank_info_form["idBankAccounts"],
            "idSystemUser": bank_info_form["idSystemUser"],
            "bankInformation":[bank_information]
            })
    response_bank={
        "idBankAccounts": bank_info_form["idBankAccounts"],
        "idSystemUser": bank_info_form["idSystemUser"],
        "idBankAccount": id_bank_account
    }

    return bankResponseEntity(response_bank)