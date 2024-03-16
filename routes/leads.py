import requests
import json
import os
import locale
import base64
import io
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from config.db import db
from utils.generateUUID import generate_UUID
from utils.slackWebhook import send_slack_message_to_lead, send_slack_message
from utils.getPDFAPI import get_pdf
from utils.formatDate import FormatDate
from utils.discountPrice import discount_deprecation, charge_appreciation
from utils.generalFunctions import generate_invoice_number
from utils.selectTemplateEmail import select_template_email

load_dotenv()

HUBSPOT_API_KEY = os.getenv("HUBSPOT_API_KEY")

lead = APIRouter()

tags_metadata = ["Leads V1"]

collection_leads = db["leads"]
collection_configs = db["configs"]


@lead.post("/api/v1/lead/create", tags=tags_metadata)
def create_lead(leadBody: dict):
    format_iso = FormatDate()

    id_lead = generate_UUID()
    # https://api.hubapi.com/crm/v3/objects/contacts
    first_name = leadBody["firstname"]
    email = leadBody["email"]
    phone = leadBody["phone"]
    message = leadBody["message"]
    created_at = format_iso.timezone_cdmx()

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
            "createdAt": created_at,
        }

        collection_leads.create_index("idLead", unique=True)
        collection_leads.insert_one(new_lead)
    except Exception as e:
        raise HTTPException(status_code=500, detail={"dbMessage": str(
            e), "errorMessage": "Hubo un error al intentar guardar el lead"})

    return {"message": "Lead created successfully", "idLead": id_lead, "idHubspot": id_hubspot}

@lead.post("/api/v2/lead/create", tags=tags_metadata)
def create_lead(leadBody: dict):
    locale.setlocale(locale.LC_ALL, 'es_MX.utf8')
    format_iso = FormatDate()


    id_lead = generate_UUID()
    # https://api.hubapi.com/crm/v3/objects/contacts
    first_name_user = leadBody["firstname"]
    email_user = leadBody["email"]
    phone_user = leadBody["phone"]
    message_user = leadBody["message"]
    created_at = format_iso.timezone_cdmx()

    id_year = leadBody["idYear"]
    id_brand = leadBody["idBrand"]
    id_model = leadBody["idModel"]
    id_version = leadBody["idVersion"]
    buy_price = leadBody["buyPrice"]
    swip_buy_price = leadBody["swipBuyPrice"]
    sell_price = leadBody["sellPrice"]
    currency_price = leadBody["currency"]

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

    message_to_hubspot_slack = f"Información de usuario \n  Nombre: {first_name_user}\n Correo: {email_user}\n Teléfono: {phone_user} \n \nInformación de Auto \n Marca: {brand}\n Modelo: {model}\n  Versión: {version}\n Año: {year} \n Precio swip: {swip_buy_currency_format} \n Precio de compra: {buy_currency_format} \n Precio de venta: {sell_currency_format} \n Moneda: {currency_price} \n \n"

    

    try:

        select_template_email(
            id_template=13,
            email_to=email_user,
            user=first_name_user,
            year=year,
            brand=brand,
            model=model,
            version=version,
            amount=swip_buy_currency_format,
        )
    except Exception as e:
        print(e)

    try:
        send_slack_message_to_lead(message_to_hubspot_slack)

    except Exception as e:
        print(e)

    try:
        car_lead = {
            "idYear": id_year,
            "idBrand": id_brand,
            "idModel": id_model,
            "idVersion": id_version,
            "buyPrice": buy_price,
            "sellPrice": sell_price,
            "swipPrice": swip_buy_price,
            "currency": currency_price,
            "year": year,
            "brand": brand,
            "model": model,
            "version": version,
        }

        new_lead = {
            "idLead": id_lead,
            "name": first_name_user,
            "email": email_user,
            "phoneNumber": phone_user,
            "message": message_user,
            "idStatus": 1,
            "created_at": created_at,
            "carInformation": car_lead,
        }
        
        collection_leads.create_index("idLead", unique=True)
        collection_leads.insert_one(new_lead)
    except Exception as e:
        raise HTTPException(status_code=500, detail={"dbMessage": str(
            e), "errorMessage": "Hubo un error al intentar actualizar el lead"})

    return {"message": "Lead updated successfully"}


@lead.get("/api/v1/lead/getAll", tags=tags_metadata)
def get_all_leads():
    leads_db = list(collection_leads.find({}, {"_id": 0, "idLead": 1, "idHubspot": 1,
                    "name": 1, "email": 1, "phoneNumber": 1, "message": 1, "idStatus": 1, "modalitySubname": 1}))
    leads_db.reverse()
    return {"data": leads_db}


@lead.get("/api/v1/lead/getById/{idLead}", tags=tags_metadata)
def get_lead_by_id(idLead: str):
    lead_db = collection_leads.find_one(
        {"idLead": idLead}, {"_id": 0, "prices": 0})
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

    try:

        select_template_email(
            id_template=13,
            email_to=email_user,
            user=first_name_user,
            year=year,
            brand=brand,
            model=model,
            version=version,
            amount=swip_buy_currency_format,
        )
    except Exception as e:
        print(e)

    try:
        send_slack_message_to_lead(message_to_hubspot_slack)

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


@lead.put("/api/v1/lead/updateCarInformation/{idLead}", tags=tags_metadata)
def update_car_information(idLead: str, leadBody: dict):
    id_lead = idLead
    id_year = leadBody["idYear"]
    id_brand = leadBody["idBrand"]
    id_model = leadBody["idModel"]
    id_version = leadBody["idVersion"]
    buy_price = leadBody["buyPrice"]
    sell_price = leadBody["sellPrice"]
    currency_price = leadBody["currency"]
    year = leadBody["year"]
    brand = leadBody["brand"]
    model = leadBody["model"]
    version = leadBody["version"]

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

    try:
        collection_leads.update_one(
            {"idLead": id_lead}, {"$set": {"carInformation": update_lead}})
    except Exception as e:
        raise HTTPException(status_code=500, detail={"dbMessage": str(
            e), "errorMessage": "Hubo un error al intentar actualizar el lead"})

    return {"message": "Car information updated successfully"}


@lead.post("/api/v1/lead/getDataQuoteById", tags=tags_metadata)
def get_data_quote_by_id(leadBody: dict):
    id_lead = leadBody["idLead"]
    invoice = leadBody["invoice"]
    result = collection_leads.find_one({"prices": {"$elemMatch": {
        "invoice": invoice}}}, {"_id": 0, "prices.$": 1})

    if result:
        return {"data": result["prices"][0]}
    else:
        return {"data": {}}


@lead.post("/api/v1/lead/generateQuote", tags=tags_metadata)
def generate_quote(leadBody: dict):
    format_iso = FormatDate()

    # pawnModality
    # sellPrice
    # buyPrice
    # sellPriceAutometric
    # buyPriceAutometric
    # typeAmountToPawn
    # amountPrice

    # print(leadBody)
    id_lead = leadBody["idLead"]



    pawn_modality = leadBody["pawnModality"]
    name_user = leadBody["name"]
    sell_price = leadBody["sellPrice"]
    buy_price = leadBody["buyPrice"]
    sell_price_autometric = leadBody["sellPriceAutometric"]
    buy_price_autometric = leadBody["buyPriceAutometric"]
    type_amount_to_pawn = leadBody["typeAmountToPawn"]
    amount_price = leadBody["amountPrice"]

    get_data_config = collection_configs.find_one({}, {"_id": 0, "gpsMonthly": 1,
                                                       "interest": 1,
                                                       "tax": 1,
                                                       "gpsInstall": 1,
                                                       "carInsurance": 1,
                                                       "referenceForInterestRate": 1,
                                                       "carGuard": 1})

    lower_buy_value = min(buy_price, buy_price_autometric)
    higher_sell_value = max(sell_price, sell_price_autometric)

    what_buy_amount_was_selected = ""
    what_sell_amount_was_selected = ""

    if lower_buy_value == buy_price:
        what_buy_amount_was_selected = "Libro Azul"
    elif lower_buy_value == buy_price_autometric:
        what_buy_amount_was_selected = "Autometrica"

    if higher_sell_value == sell_price:
        what_sell_amount_was_selected = "Libro Azul"
    elif higher_sell_value == sell_price_autometric:
        what_sell_amount_was_selected = "Autometrica"

    amount_to_finance = 0
    modality_subname = ""
    amount_monthly_guard = 0
    amount_monthly_gps = 0
    amount_monthly_gps_install = 0
    amount_monthly_insurance = 0
    amount_to_deposit = 0
    interest_rate = 0
    amount_monthly_interest_rate = 0
    tax_rate = get_data_config["tax"]
    amount_monthly_total_with_tax = 0
    amount_monthly_total = 0
    has_gps = False
    created_at = format_iso.timezone_cdmx()

    result = collection_configs.find_one({"modalities": {"$elemMatch": {
                                         "idModality": pawn_modality}}}, {"_id": 0, "modalities.$": 1})

    if result:
        modality = result["modalities"][0]
        has_gps = modality["hasGPS"]
        modality_subname = modality["subnameModality"]

        get_percentages = modality["percentages"]

        # reglas de negocio
        if type_amount_to_pawn != "00000000-0000-0000-0000-000000000000":
            find_id_percentage = next(
                (item for item in get_percentages if item["idPercentage"] == type_amount_to_pawn), None)

            if find_id_percentage:
                amount_to_finance = find_id_percentage["percent"] * \
                    lower_buy_value
        else:
            amount_to_finance = amount_price

        reference_for_interest_rate = get_data_config["referenceForInterestRate"]

        if has_gps == True:
            amount_monthly_gps_install = get_data_config["gpsInstall"]
            amount_monthly_insurance = 0  # get_data_config["carInsurance"]
            amount_monthly_gps = get_data_config["gpsMonthly"]
            amount_to_deposit = amount_to_finance - amount_monthly_gps_install

            if reference_for_interest_rate and amount_to_finance >= reference_for_interest_rate:
                interest_rate = modality["interestRateMin"]
            elif reference_for_interest_rate and amount_to_finance < reference_for_interest_rate:
                interest_rate = modality["interestRateMax"]
        else:
            amount_monthly_guard = get_data_config["carGuard"]
            amount_to_deposit = amount_to_finance

            if reference_for_interest_rate and amount_to_finance >= reference_for_interest_rate:
                interest_rate = modality["interestRateMin"]
            elif reference_for_interest_rate and amount_to_finance < reference_for_interest_rate:
                interest_rate = modality["interestRateMax"]
        # terminan reglas de negocio

        # calculos de negocio
        amount_monthly_interest_rate = amount_to_finance * interest_rate
        amount_monthly_total = amount_monthly_insurance + amount_monthly_gps + \
            amount_monthly_guard + amount_monthly_interest_rate
        amount_monthly_total_with_tax = charge_appreciation(
            amount_monthly_total, tax_rate)

        data_to_frontend = {
            "pawnModality": pawn_modality,
            "sellPrice": sell_price,
            "buyPrice":     buy_price,
            "sellPriceAutometric": sell_price_autometric,
            "buyPriceAutometric": buy_price_autometric,
            "typeAmountToPawn": type_amount_to_pawn,
            "amountPrice": amount_price,
            "amountToFinance": amount_to_finance,
            "modalitySubname": modality_subname,
            "amountMonthlyGuard": amount_monthly_guard,
            "amountMonthlyGps": amount_monthly_gps,
            "amountMonthlyGpsInstall": amount_monthly_gps_install,
            "amountMonthlyInsurance": amount_monthly_insurance,
            "amountToDeposit": amount_to_deposit,
            "interestRate": interest_rate,
            "amountMonthlyInterestRate": amount_monthly_interest_rate,
            "taxRate": tax_rate,
            "amountMonthlyTotalWithTax": amount_monthly_total_with_tax,
            "amountMonthlyTotal": amount_monthly_total,
            "hasGps": has_gps,
            "whatBuyAmountWasSelected": what_buy_amount_was_selected,
            "whatSellAmountWasSelected": what_sell_amount_was_selected,
            "idModality": pawn_modality,
            "amountAppraisal": lower_buy_value,
            "createdAt": created_at,
        }

        if pawn_modality == "e9c6b545-a4a6-4243-a651-84116cbb739d":
            invoice = generate_invoice_number("PRESTP", id_lead)
            data_to_frontend["invoice"] = invoice

        if pawn_modality == "e3a6f8b8-7b7a-4551-888c-7845c8575e00":
            invoice = generate_invoice_number("PRECTP", id_lead)
            data_to_frontend["invoice"] = invoice

        collection_leads.update_one(
            {"idLead": id_lead}, {"$set": {"name": name_user,"invoice": data_to_frontend["invoice"], "idModality": data_to_frontend["idModality"], "modalitySubname": data_to_frontend["modalitySubname"], "idStatus": 2, }, "$addToSet": {"prices": data_to_frontend}})

        # if type_amount_to_pawn == "sellPrice":
        #     amount_to_finance = sell_price
        # elif type_amount_to_pawn == "buyPrice":
        #     amount_to_finance = buy_price
        # elif type_amount_to_pawn == "sellPriceAutometric":
        #     amount_to_finance = sell_price_autometric
        # elif type_amount_to_pawn == "buyPriceAutometric":
        #     amount_to_finance = buy_price_autometric
        # elif type_amount_to_pawn == "amountPrice":
        #     amount_to_finance = amount_price

        # if modality["idModality"] == 1:
        #     amount_to_finance = charge_appreciation(amount_to_finance, 0.15)
        # elif modality["idModality"] == 2:
        #     amount_to_finance = discount_deprecation(amount_to_finance, 0.15)
    # print(result)

    return {"message": "Cotización generada correctamente", "data": data_to_frontend}


@lead.post("/api/v1/lead/generatePrice", tags=tags_metadata)
def generate_price(leadBody: dict):
    locale.setlocale(locale.LC_ALL, 'es_MX.utf8')

    id_modality = leadBody["idModality"]
    name_price = leadBody["namePrice"]
    format_date = FormatDate()
    date_format = format_date.date_format_now()
    date_end = format_date.last_day_of_month()

    data_to_pdf = {"priceAt": date_format,
                   "name" : leadBody["name"],
                   "priceEndAt": date_end,
                   "vehicleType": "Automóvil",
                   "brand": leadBody["brand"],
                   "invoice": leadBody["invoice"],
                   "model": leadBody["model"],
                   "year": leadBody["year"],
                   "version": leadBody["version"],
                   "namePrice": name_price,
                   "amountToFinance": leadBody["amountToFinance"],
                   "modalitySubname": leadBody["modalitySubname"],
                   "amountMonthlyGuard": leadBody["amountMonthlyGuard"],
                   "amountMonthlyGps": leadBody["amountMonthlyGps"],
                   "amountMonthlyGpsInstall": leadBody["amountMonthlyGpsInstall"],
                   "amountMonthlyInsurance": leadBody["amountMonthlyInsurance"],
                   "amountToDeposit": leadBody["amountToDeposit"],
                   "interestRate": leadBody["interestRate"] * 100,
                   "amountMonthlyInterestRate": leadBody["amountMonthlyInterestRate"],
                   "taxRate": leadBody["taxRate"] * 100,
                   "amountMonthlyTotalWithTax": leadBody["amountMonthlyTotalWithTax"],
                   "amountMonthlyTotal": leadBody["amountMonthlyTotal"],
                   "idModality": leadBody["idModality"],
                   "amountAppraisal": leadBody["amountAppraisal"]}

    try:
        if id_modality == "e9c6b545-a4a6-4243-a651-84116cbb739d":

            result = get_pdf(data_to_pdf, "959242", "PreCotizacion_GPS")
            result_path = result["path"]

            try:
                pdf_content = base64.b64decode(result_path)
                return StreamingResponse(io.BytesIO(pdf_content), media_type="application/pdf", headers={"Content-Disposition": "inline; filename=Precotizacion_GPS.pdf"})

            except Exception as e:
                print(str(e))
                raise HTTPException(status_code=500, detail=str(e))

            # return {"message": "Cotización generada correctamente", "data": data_to_pdf}

        if id_modality == "e3a6f8b8-7b7a-4551-888c-7845c8575e00":

            result = get_pdf(data_to_pdf, "959245", "PreCotizacion_Resguardo")
            result_path = result["path"]

            try:
                pdf_content = base64.b64decode(result_path)
                return StreamingResponse(io.BytesIO(pdf_content), media_type="application/pdf", headers={"Content-Disposition": "inline; filename=Precotizacion_Resguardo.pdf"})

            except Exception as e:
                print(str(e))
                raise HTTPException(status_code=500, detail=str(e))

        # return {"message": "Cotización generada correctamente", "data": data_to_pdf}

    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=500, detail={"dbMessage": str(
            e), "errorMessage": "Hubo un error al intentar generar el pdf"})


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
