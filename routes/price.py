import requests
import json
import os
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Header
from utils.generateUUID import generate_UUID
from utils.discountPrice import discount_deprecation

load_dotenv()

LIBRO_AZUL_USER = os.getenv("LIBRO_AZUL_USER")
LIBRO_AZUL_PASSWORD = os.getenv("LIBRO_AZUL_PASSWORD")
LIBRO_AZUL_ENDPOINT = os.getenv("LIBRO_AZUL_ENDPOINT")

price = APIRouter()

tags_metadata = ["Price V1"]


@price.get("/api/v1/price/getToken", tags=tags_metadata)
def create_lead():
    try:
        response = requests.post(
            url=f"{LIBRO_AZUL_ENDPOINT}/api/Sesion?Usuario={LIBRO_AZUL_USER}&Contrasena={LIBRO_AZUL_PASSWORD}",
            headers={
                "Content-Type": "application/json"
            },
            data="{}"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail={"errorMessage": str(
            e), })

    return {"token": response.json()}

@price.get("/api/v1/price/getYears", tags=tags_metadata)
def get_years(x_key_book: str = Header(default=None)):
    try:
        response = requests.post(
            url=f"{LIBRO_AZUL_ENDPOINT}/api/Años/?Llave={x_key_book}",
            headers={
                "Content-Type": "application/json"
            },
            data=None
        )

        response_json = response.json()

        response_transform =[
            {"id": elemento["Clave"], "text": elemento["Nombre"]} 
            for elemento in response_json
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail={"errorMessage": str(
            e), })

    return {"result": response_transform}

@price.post("/api/v1/price/getBrands", tags=tags_metadata)
def get_brands(data_price: dict, x_key_book: str = Header(default=None)):
    try:
        year = data_price["idYear"]
        response = requests.post(
            url=f"{LIBRO_AZUL_ENDPOINT}/api/Marcas/?Llave={x_key_book}&ClaveAnio={year}",
            headers={
                "Content-Type": "application/json"
            },
            data=None
        )

        response_json = response.json()

        response_transform =[
            {"id": elemento["Clave"], "text": elemento["Nombre"]} 
            for elemento in response_json
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail={"errorMessage": str(
            e), })

    return {"result": response_transform}

@price.post("/api/v1/price/getModels", tags=tags_metadata)
def get_models(data_price: dict, x_key_book: str = Header(default=None)):
    try:
        year = data_price["idYear"]
        brand = data_price["idBrand"]
        response = requests.post(
            url=f"{LIBRO_AZUL_ENDPOINT}/Api/Modelos/?Llave={x_key_book}&ClaveAnio={year}&ClaveMarca={brand}",
            headers={
                "Content-Type": "application/json"
            },
            data=None
        )

        response_json = response.json()

        response_transform =[
            {"id": elemento["Clave"], "text": elemento["Nombre"]} 
            for elemento in response_json
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail={"errorMessage": str(
            e), })

    return {"result": response_transform}

@price.post("/api/v1/price/getVersions", tags=tags_metadata)
def get_versions(data_price: dict, x_key_book: str = Header(default=None)):
    try:
        year = data_price["idYear"]
        brand = data_price["idBrand"]
        model = data_price["idModel"]
        response = requests.post(
            url=f"{LIBRO_AZUL_ENDPOINT}/Api/Versiones/?Llave={x_key_book}&ClaveAnio={year}&ClaveMarca={brand}&ClaveModelo={model}",
            headers={
                "Content-Type": "application/json"
            },
            data=None
        )

        response_json = response.json()

        response_transform =[
            {"id": elemento["Clave"], "text": elemento["Nombre"]} 
            for elemento in response_json
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail={"errorMessage": str(
            e), })

    return {"result": response_transform}

@price.post("/api/v1/price/getPrice", tags=tags_metadata)
def get_price(data_price: dict, x_key_book: str = Header(default=None)):
    try:
        version = data_price["idVersion"]
        response = requests.post(
            url=f"{LIBRO_AZUL_ENDPOINT}/Api/Precio/?Llave={x_key_book}&ClaveVersion={version}",
            headers={
                "Content-Type": "application/json"
            },
            data=None
        )

        response_json = response.json()

        swip_price  = 0

        try:
            discount_adjustment_market = discount_deprecation(response_json["Compra"], 0.15)
            swip_price = discount_adjustment_market * 0.8


        except ValueError:
            print("Error: El valor_original no es un número válido.")

        print(swip_price)

        response_result = {
            "sellPrice": response_json["Venta"],
            "buyPrice": response_json["Compra"],
            "currency": response_json["Moneda"],
            "swipBuyPrice": swip_price,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail={"errorMessage": str(
            e), })

    return {"result": response_result}

@price.post("/api/v1/price/getBuyPrice", tags=tags_metadata)
def get_price(data_price: dict, x_key_book: str = Header(default=None)):
    try:
        version = data_price["version"]
        response = requests.post(
            url=f"{LIBRO_AZUL_ENDPOINT}/Api/Precio/?Llave={x_key_book}&ClaveVersion={version}",
            headers={
                "Content-Type": "application/json"
            },
            data=None
        )

        response_json = response.json()

        swip_price  = 0

        try:
            discount_adjustment_market = discount_deprecation(response_json["Compra"], 0.15)
            swip_price = discount_adjustment_market * 0.8


        except ValueError:
            print("Error: El valor_original no es un número válido.")

        response_result = {
            "buyPrice": response_json["Compra"],
            "currency": response_json["Moneda"],
            "swipBuyPrice": swip_price,
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail={"errorMessage": str(
            e), })

    return {"result": response_result}
