from pydantic import BaseModel
from typing import Optional

class SetNewLoans(BaseModel):
    idBankAccount: str
    idSystemUser: str
    idProcesses: str
    idProcess: Optional[str]
    idLoans: str
    requestedAt: str
    concept: str
    amountMonthly: int
    amountLoan: int
    amountIva: int
    amountInterest: int
    amountPayOff: int
    nextPaymentAt: str
    offset: Optional[str]

class ResponseNewLoans(BaseModel):
    idLoan: str
    idSystemUser: str