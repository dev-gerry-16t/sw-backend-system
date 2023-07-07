from pydantic import BaseModel

class SetNewEmailTemplate (BaseModel):
    templateName: str
    templateSubject: str
    templateText: str
    templateHtml: str