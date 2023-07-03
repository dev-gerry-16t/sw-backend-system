from pydantic import BaseModel

class SetNewBank(BaseModel):
    idBankAccounts: str
    idSystemUser: str
    beneficiary: str
    numberAccount: str
    clabe: str
    bank: str

class ResponseNewBank(BaseModel):
    idBankAccounts: str
    idBankAccount: str
    idSystemUser: str