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


