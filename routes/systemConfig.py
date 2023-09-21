from fastapi import APIRouter, UploadFile, File, HTTPException
from config.awsConfig import session
from config.db import db
from utils.email import Email
from models.systemConfig import SetNewEmailTemplate

system = APIRouter()

tags_metadata = ["System Config V1"]
collection_admins = db["adminUsers"]


@system.post("/api/v1/system/templateEmail/create", tags=tags_metadata)
def create_template_email(bodyConfig: SetNewEmailTemplate):
    email_conf = Email()
    dict_body_config = dict(bodyConfig)

    response = email_conf.create_template_email(
        template_name=dict_body_config["templateName"],
        template_subject=dict_body_config["templateSubject"],
        template_text=dict_body_config["templateText"],
        template_html=dict_body_config["templateHtml"],
    )

    return response


@system.put("/api/v1/system/templateEmail/update", tags=tags_metadata)
def update_template_email(bodyConfig: SetNewEmailTemplate):
    email_conf = Email()
    dict_body_config = dict(bodyConfig)

    response = email_conf.update_template_email(
        template_name=dict_body_config["templateName"],
        template_subject=dict_body_config["templateSubject"],
        template_text=dict_body_config["templateText"],
        template_html=dict_body_config["templateHtml"],
    )

    return response


@system.post("/api/v1/system/templateEmail/test", tags=tags_metadata)
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
        template_name=template_name,
        email_to=email_to,
        email_from=email_from,
        template_data=template_data
    )

    return response


@system.post("/api/v1/system/login/admin", tags=tags_metadata)
async def login_admin(file: UploadFile = File(...)):

    client_rekognition = session.client('rekognition')
    # client_s3 = session.client('s3')
    contents = await file.read()

    users = list(collection_admins.find({}, {"_id": 0}))
    # users = ["433e82a6-7eb1-4dc9-b2e6-73c373797291", "4a4ca505-36f2-4a41-8832-5afbf4591733", "7f3175be-09dc-4d97-83b2-cacc95b76669", "8978816d-f24f-4402-819c-68ef8c02e284"]

    info_user = {}

    for user in users:
        response =  client_rekognition.compare_faces(
        SourceImage={
            'S3Object': {
                'Bucket': 'swiputils',
                'Name': user["idAdmin"]
            }
        },
        TargetImage={
            'Bytes': contents,
        },
        SimilarityThreshold=70,
        QualityFilter='AUTO'
        )

        if response is not None:
            face_matches = response['FaceMatches']
            if len(face_matches) != 0:
                face_match = face_matches[0]
                similarity = face_match['Similarity']
                if similarity >= 70:
                    # info_document= client_s3.get_object(
                    #     Bucket='swiputils',
                    #     Key=user["idAdmin"]
                    # )
                    name_user = user['name']
                    email_user = user['email']
                    info_user = {"name": name_user, "idAdmin": user["idAdmin"], "email": email_user}
                    return {"filename": file.filename, **info_user}

    raise HTTPException(status_code=500, detail="No se encontro coincidencia")
