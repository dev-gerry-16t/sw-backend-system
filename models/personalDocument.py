from typing import List, Optional
from pydantic import BaseModel

class Screen(BaseModel):
    idScreen: str
    path: Optional[str]
    nextPath: Optional[str]
    idDocumentType: str
    name: str
    description: str
    type: str
    capture: bool
    accept: str
    label: str
    bucketSource: str
    index: int

class ResponseModelScreen(BaseModel):
    screens: List[Screen]

class DataRequestDocument(BaseModel):
    idScreen: str
    idDocumentType: int
    bucketSource: str
