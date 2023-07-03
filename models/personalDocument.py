from typing import List
from pydantic import BaseModel

class Screen(BaseModel):
    idScreen: str
    path: str
    nextPath: str
    idDocumentType: str
    name: str
    description: str
    type: str
    capture: bool
    accept: str
    label: str
    bucketSource: str

class ResponseModelScreen(BaseModel):
    screens: List[Screen]

class DataRequestDocument(BaseModel):
    idScreen: str
    idDocumentType: int
    bucketSource: str
