from pydantic import BaseModel

class SetNewProfile(BaseModel):
    idProfile: str
    idSystemUser: str
    name: str
    dateOfBirth: str
    curp: str
    rfc: str
    numberId: str
    street: str
    neighborhood: str
    zipCode: str
    city: str
    state: str
    country: str

class ResponseNewProfile(BaseModel):
    idProfile: str
    idSystemUser: str