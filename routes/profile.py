from fastapi import APIRouter
from models.profile import SetNewProfile, ResponseNewProfile
from config.db import db
from schemas.profile import profileResponseEntity

profileRouter = APIRouter()

tags_metadata = ["Profile V1"]

collection_profile_information = db["profiles"]

@profileRouter.post("/api/v1/profile/create", response_model= ResponseNewProfile ,tags = tags_metadata)
def create_profile_information(profileBody: SetNewProfile):
    profile_info_form = dict(profileBody)

    profile_information = {
        "name": profile_info_form["name"],
        "dateOfBirth": profile_info_form["dateOfBirth"],
        "curp": profile_info_form["curp"],
        "rfc": profile_info_form["rfc"],
        "numberId": profile_info_form["numberId"],
    }

    address_information = {
        "street": profile_info_form["street"],
        "neighborhood": profile_info_form["neighborhood"],
        "zipCode": profile_info_form["zipCode"],
        "city": profile_info_form["city"],
        "state": profile_info_form["state"],
        "country": profile_info_form["country"],
    }

    collection_profile_information.create_index("idSystemUser", unique=True)
    collection_profile_information.insert_one({
            "idProfile": profile_info_form["idProfile"],
            "idSystemUser": profile_info_form["idSystemUser"],
            "profileInformation": profile_information,
            "addressInformation":[address_information]
            })

    return profileResponseEntity(id_profile=profile_info_form["idProfile"], id_system_user= profile_info_form["idSystemUser"])
