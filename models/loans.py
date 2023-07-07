from pydantic import BaseModel

class SetNewLoans(BaseModel):
    idBankAccount: str
    idSystemUser: str
    idProcesses: str
    idProcess: str
    idLoans: str
    requestedAt: str
    concept: str
    amountMonthly: int
    amountLoan: int
    amountIva: int
    amountInterest: int
    amountPayOff: int
    nextPaymentAt: str

class ResponseNewLoans(BaseModel):
    idLoan: str
    idSystemUser: str