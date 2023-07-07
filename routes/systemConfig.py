from fastapi import APIRouter
from utils.email import Email
from models.systemConfig import SetNewEmailTemplate

system = APIRouter()

tags_metadata = ["System Config V1"]

@system.post("/api/v1/system/templateEmail/create", tags = tags_metadata)
def create_template_email(bodyConfig: SetNewEmailTemplate):
    email_conf = Email()
    dict_body_config = dict(bodyConfig)

    response = email_conf.create_template_email(
        template_name = dict_body_config["templateName"],
        template_subject = dict_body_config["templateSubject"],
        template_text = dict_body_config["templateText"],
        template_html = dict_body_config["templateHtml"],
    )

    return response

@system.post("/api/v1/system/templateEmail/test", tags = tags_metadata)
def test_template_email(bodyConfig: dict):
    email_conf = Email()

    template_name = bodyConfig["templateName"]
    email_to = bodyConfig["emailTo"]
    email_from = bodyConfig["emailFrom"]
    template_data = {
        "user": bodyConfig["user"],
        "amountApprovedCredit": bodyConfig["amountApprovedCredit"],
    }

    response = email_conf.send_email_template(
        template_name = template_name,
        email_to = email_to,
        email_from = email_from,
        template_data = template_data
    )

    return response
