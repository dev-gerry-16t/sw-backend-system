import requests
import json
import os
import locale
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from config.db import db
from utils.generateUUID import generate_UUID
from utils.slackWebhook import send_slack_message_to_lead, send_slack_message
from utils.getPDFAPI import get_pdf
from utils.formatDate import FormatDate
from utils.discountPrice import discount_deprecation, charge_appreciation
from utils.generalFunctions import generate_invoice_number

load_dotenv()

HUBSPOT_API_KEY = os.getenv("HUBSPOT_API_KEY")

lead = APIRouter()

tags_metadata = ["Leads V1"]

collection_leads = db["leads"]


@lead.post("/api/v1/lead/create", tags=tags_metadata)
def create_lead(leadBody: dict):
    id_lead = generate_UUID()
    # https://api.hubapi.com/crm/v3/objects/contacts
    first_name = leadBody["firstname"]
    email = leadBody["email"]
    phone = leadBody["phone"]
    message = leadBody["message"]
    try:
        response = requests.post(
            url="https://api.hubapi.com/crm/v3/objects/contacts",
            headers={
                "Authorization": "Bearer " + HUBSPOT_API_KEY,
                "Content-Type": "application/json"
            },
            data=json.dumps({
                "properties": {
                    "email": email,
                    "firstname": first_name,
                    "phone": phone,
                    "message": message
                }
            })
        )

        id_hubspot = response.json()["id"]

        new_lead = {
            "idLead": id_lead,
            "idHubspot": id_hubspot,
            "name": first_name,
            "email": email,
            "phoneNumber": phone,
            "message": message,
            "idStatus": 1,
        }

        collection_leads.create_index("idLead", unique=True)
        collection_leads.insert_one(new_lead)
    except Exception as e:
        raise HTTPException(status_code=500, detail={"dbMessage": str(
            e), "errorMessage": "Hubo un error al intentar guardar el lead"})

    return {"message": "Lead created successfully", "idLead": id_lead, "idHubspot": id_hubspot}


@lead.get("/api/v1/lead/getAll", tags=tags_metadata)
def get_all_leads():
    leads_db = list(collection_leads.find({}, {"_id": 0, "idLead": 1, "idHubspot": 1,
                    "name": 1, "email": 1, "phoneNumber": 1, "message": 1, "idStatus": 11}))
    leads_db.reverse()
    return {"data": leads_db}


@lead.get("/api/v1/lead/getById/{idLead}", tags=tags_metadata)
def get_lead_by_id(idLead: str):
    lead_db = collection_leads.find_one({"idLead": idLead}, {"_id": 0 })
    return {"data": lead_db}


@lead.put("/api/v1/lead/update", tags=tags_metadata)
def update_lead(leadBody: dict):
    locale.setlocale(locale.LC_ALL, 'es_MX.utf8')

    id_lead = leadBody["idLead"]
    id_hubspot = leadBody["idHubspot"]

    id_year = leadBody["idYear"]
    id_brand = leadBody["idBrand"]
    id_model = leadBody["idModel"]
    id_version = leadBody["idVersion"]
    buy_price = leadBody["buyPrice"]
    swip_buy_price = leadBody["swipBuyPrice"]
    sell_price = leadBody["sellPrice"]
    currency_price = leadBody["currency"]
    email_user = leadBody["email"]
    first_name_user = leadBody["firstname"]
    phone_user = leadBody["phone"]
    message_user = leadBody["message"]

    buy_currency_format = ""
    swip_buy_currency_format = ""
    sell_currency_format = ""

    try:
        buy_int_price = int(buy_price)
        buy_currency_format = locale.currency(
            buy_int_price, grouping=True, symbol=True)
        buy_currency_format += f" {currency_price}"

        sell_int_price = int(sell_price)
        sell_currency_format = locale.currency(
            sell_int_price, grouping=True, symbol=True)
        sell_currency_format += f" {currency_price}"

        swip_buy_int_price = int(swip_buy_price)
        swip_buy_currency_format = locale.currency(
            swip_buy_int_price, grouping=True, symbol=True)
        swip_buy_currency_format += f" {currency_price}"

    except ValueError:
        print("Error: El valor_original no es un número válido.")

    year = leadBody["year"]
    brand = leadBody["brand"]
    model = leadBody["model"]
    version = leadBody["version"]

    message_to_hubspot = f"Información de Auto \n Marca: {brand} \n Modelo: {model} \n Versión: {version} \n Año: {year} \n Precio swip: {swip_buy_currency_format} \n Precio de compra: {buy_currency_format} \n Precio de venta: {sell_currency_format} \n Moneda: {currency_price} \n \n"

    message_to_hubspot_slack = f"Información de usuario \n  Nombre: {first_name_user}\n Correo: {email_user}\n Teléfono: {phone_user} \n \nInformación de Auto \n Marca: {brand}\n Modelo: {model}\n  Versión: {version}\n Año: {year} \n Precio swip: {swip_buy_currency_format} \n Precio de compra: {buy_currency_format} \n Precio de venta: {sell_currency_format} \n Moneda: {currency_price} \n \n"

    data_properties = {
        "properties": {
            "message": message_to_hubspot
        }
    }

    # format_date = FormatDate()
    # date_format = format_date.date_format_now()

    # invoice_number = generate_invoice_number(id_lead, id_hubspot)

    # appraisal_amount = discount_deprecation(buy_price, 0.15)
    # swip_amount = appraisal_amount * 0.8
    # monthly_monitoring = 490
    # minimum_loan = 20000
    # month_tax = 0.079
    # total_interest_revolve = minimum_loan * month_tax
    # total_tax = total_interest_revolve * 0.16
    # total_month = total_interest_revolve + total_tax
    # install_gps = 500

    # total_gps_financing = appraisal_amount - (monthly_monitoring + install_gps)
    # monthly_gps_tax = 0.079
    # total_gps_interest = appraisal_amount * monthly_gps_tax
    # total_gps_tax = total_gps_interest * 0.16
    # total_gps_month = total_gps_interest + total_gps_tax

    # financing_guard_amount = int(buy_price)
    # monthly_guard = 1500
    # total_guard_financing = financing_guard_amount - monthly_guard
    # month_guard_tax = 0.05
    # total_guard_interest = financing_guard_amount * month_guard_tax
    # total_guard_tax = total_guard_interest * 0.16
    # total_guard_month = total_guard_interest + total_guard_tax

    # data_to_pdf = {
    #     "invoice": invoice_number,
    #     "priceAt": date_format,
    #     "vehicleType": "Automóvil",
    #     "appraisalAmount": appraisal_amount,
    #     "brand": brand,
    #     "model": model,
    #     "year": year,
    #     "version": version,
    #     "swipAmount": swip_amount,
    #     "monthlyMonitoring": monthly_monitoring,
    #     "minimumLoan": minimum_loan,
    #     "monthTax": month_tax * 100,
    #     "totalInterest": total_interest_revolve,
    #     "totalTax": total_tax,
    #     "totalMonth": total_month,
    #     "installGPS": install_gps,
    #     "financingAmount": appraisal_amount,
    #     "monthlyMonitoring": monthly_monitoring,
    #     "totalGPSFinancing": total_gps_financing,
    #     "monthGPSTax": monthly_gps_tax * 100,
    #     "totalGPSInterest": total_gps_interest,
    #     "totalGPSTax": total_gps_tax,
    #     "totalGPSMonth": total_gps_month,
    #     "financingGuardAmount": financing_guard_amount,
    #     "monthlyGuard": monthly_guard,
    #     "totalGuardFinancing": total_guard_financing,
    #     "monthGuardTax": month_guard_tax * 100,
    #     "totalGuardInterest": total_guard_interest,
    #     "totalGuardTax": total_guard_tax,
    #     "totalGuardMonth": total_guard_month,
    #     "amountGuard": monthly_guard,

    # }

    try:
        # result = get_pdf(data_to_pdf, "933947", "Cotizacion_Swip")
        # result_path = result["path"]
        # attachments = [
        #     {"fallback": "fallback",
        #      "pretext": "Descarga el pdf y envialo a al lead",
        #      "title": "Click para ver el pdf",
        #      "title_link": result_path,
        #      "text": "Pre cotización"
        #      }
        # ]
        send_slack_message_to_lead(message_to_hubspot_slack)

        # send_slack_message_to_lead(message_to_hubspot_slack, attachments)
    except Exception as e:
        print(e)

    try:
        response = requests.patch(
            url=f"https://api.hubapi.com/crm/v3/objects/contacts/{id_hubspot}",
            headers={
                "Authorization": "Bearer " + HUBSPOT_API_KEY,
                "Content-Type": "application/json"
            },
            data=json.dumps(data_properties)
        )

        update_lead = {
            "idYear": id_year,
            "idBrand": id_brand,
            "idModel": id_model,
            "idVersion": id_version,
            "buyPrice": buy_price,
            "sellPrice": sell_price,
            "currency": currency_price,
            "year": year,
            "brand": brand,
            "model": model,
            "version": version,
        }

        collection_leads.update_one(
            {"idLead": id_lead}, {"$set": {"carInformation": update_lead}})
    except Exception as e:
        raise HTTPException(status_code=500, detail={"dbMessage": str(
            e), "errorMessage": "Hubo un error al intentar actualizar el lead"})

    return {"message": "Lead updated successfully"}


@lead.post("/api/v1/lead/testpdf", tags=tags_metadata)
def test_pdf(leadBody: dict):

    appraisal_amount = leadBody["appraisalAmount"]
    brand = leadBody["brand"]
    model = leadBody["model"]
    version = leadBody["version"]
    year = leadBody["year"]
    vehicle_type = leadBody["vehicleType"]
    swip_amount = leadBody["swipAmount"]
    month_tax = leadBody["monthTax"]
    invoice = leadBody["invoice"]
    price_at = leadBody["priceAt"]

    data = {
        "appraisalAmount": appraisal_amount,
        "brand": brand,
        "model": model,
        "version": version,
        "year": year,
        "vehicleType": vehicle_type,
        "swipAmount": swip_amount,
        "monthTax": month_tax * 100,
        "invoice": invoice,
        "priceAt": price_at,
    }

    result = {}

    try:
        result = get_pdf(data, "933947", "Cotizacion_Swip")
    except Exception as e:
        raise HTTPException(status_code=500, detail={"dbMessage": str(
            e), "errorMessage": "Hubo un error al intentar generar el pdf"})

    return result
