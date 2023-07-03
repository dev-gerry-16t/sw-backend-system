from fastapi import APIRouter
from config.db import db
from models.carInformation import SetCarInformation, ResponseNewCarInformation
from utils.generateUUID import generate_UUID
from schemas.carInformation import carInfoResponseEntity, setCarInfoEntity

carInfo = APIRouter()

tags_metadata = ["Car Information V1"]

collection_car_information = db["carInformation"]

@carInfo.post("/api/v1/carInfo/create", response_model= ResponseNewCarInformation ,tags = tags_metadata)
def create_car_information(carInfo: SetCarInformation):
    car_info_form = dict(carInfo)
    id_car = generate_UUID()

    collection_car_information.create_index("idCarInformation", unique=True)
    collection_car_information.insert_one(setCarInfoEntity(id_car, car_info_form))

    return carInfoResponseEntity(id_car=id_car, id_system_user= car_info_form["idSystemUser"])
