from pydantic import BaseModel

class SetCarInformation(BaseModel):
    idSystemUser: str
    brand: str
    model: str
    type: str
    transmissionType: str
    color: str
    year: str
    mileage: str
    amountPrice: int
    plateState: str

class ResponseNewCarInformation(BaseModel):
    idCarInformation: str
    idSystemUser: str