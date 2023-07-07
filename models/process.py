from pydantic import BaseModel
from typing import Optional, List, Union

class SetNewProcess(BaseModel):
    idCarInformation: str
    idCarDocuments: str
    idLoans: str
    idProcesses: Optional[str]
    idSystemUser: str

class ResponseNewProcess(BaseModel):
    idProcesses: str
    idProcess: str
    idSystemUser: str

class ObjectResponseAllProcess(BaseModel):
    idProcesses: str
    idProcess: str
    idSystemUser: str
    name: str
    createdAt: str
    idStatus: str
    processes: int
    amountApprovedCredit: int
    approvedAt: Union[str, None]
    loansRequested: int

class ResponseAllProcess(BaseModel):
    data: List[ObjectResponseAllProcess]

class ResponseProcessById(BaseModel):
    idProcesses: str
    idSystemUser: str
    idProcess: str
    idStatus: int
    amountAvailable: int
    amountApprovedCredit: int
    isApproved: bool
    approvedById: Union[str, None]
    approvedAt: Union[str, None]
    createdAt: str
    updatedAt: Union[str, None]
    idLoans: str
    idCarDocuments: str
    idCarInformation: str    

class ListAddress(BaseModel):
    street: str
    neighborhood: str
    zipCode: str
    city: str
    state: str
    country: str

class ResponseGetPersonalInfo(BaseModel):
    email: str
    phoneNumber: str
    name: str
    dateOfBirth: str
    curp: str
    rfc: str
    numberId: str
    addressInformation: List[ListAddress]

class ResponseGetCarInfo(BaseModel):
    brand: str
    model: str
    type: str
    transmissionType: str
    color: str
    year: str
    mileage: str
    amountPrice: int
    plateState: str

class ResponseGetBankInfo(BaseModel):
    idBankAccount: str
    beneficiary: str
    numberAccount: str
    clabe: str
    bank: str

class RequestUpdateProcessById(BaseModel):
    idSystemUser: str
    amountApprovedCreditFormatted: Union[str, None]
    idStatus: Union[int, None]
    amountAvailable: Union[int, None]
    amountApprovedCredit: Union[int, None]
    isApproved: Union[bool, None]
    approvedById: Union[str, None]
    approvedAt: Union[str, None]
    updatedAt: Union[str, None]



