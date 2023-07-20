from pydantic import BaseModel
from typing import Union

class SetUser(BaseModel):
    idSystemUser: str
    idAddresses: str
    idProcesses: str
    idPersonalDocuments: str
    idProfile: str
    idBankAccounts: str
    email: str
    validateCode: str
    phoneNumber: str
    password: str
    idUserType: int
    registerAt: str
    lastLogin: str
    screenNumber: int

class ResponseNewUser(BaseModel):
    id: str
    idSystemUser: str
    idAddresses: str
    idProcesses: str
    idPersonalDocuments: str
    idProfile: str
    idBankAccounts: str
    idUserType: int
    screenNumber: int
    idLoans: str

class ResponseProgress(BaseModel):
    nextScreen: int

class NewUser(BaseModel):
    email: str
    phoneNumber: str
    password: str
    idUserType: int
    screenNumber: int

class Login(BaseModel):
    email: str
    password: str
    offset:str

class ResponseLogin(BaseModel):    
    email:str;
    phoneNumber:str;
    idUserType:int;
    screenNumber:int;
    idSystemUser:str;
    idAddresses:str;
    idProcesses:str;
    idPersonalDocuments:str;
    idProfile:str;
    idBankAccounts:str;
    lastLoginAt: Union[str, None];
    path:str;
    token: str