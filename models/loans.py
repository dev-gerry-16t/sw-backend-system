from pydantic import BaseModel
from typing import Optional

class SetNewLoans(BaseModel):
    idBankAccount: str
    idSystemUser: str
    idProcesses: str
    idLoanType: Optional[int]
    idProcess: Optional[str]
    idLoans: str
    idStatus: Optional[int]
    concept: str
    amountMonthly: int
    amountLoan: int
    amountIva: int
    amountInterest: int
    amountPayOff: int
    offset: Optional[str]

class ResponseNewLoans(BaseModel):
    idLoan: str
    idSystemUser: str