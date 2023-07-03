from pydantic import BaseModel

class SetNewLoans(BaseModel):
    idLoans: str
    idSystemUser: str

class ResponseNewLoans(BaseModel):
    idLoans: str
    idSystemUser: str