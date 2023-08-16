import stripe
import os
import datetime
import pytz
from fastapi import APIRouter, HTTPException, Header, Request
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv
from config.db import db
from utils.generateUUID import generate_UUID
from utils.formatDate import FormatDate


load_dotenv()

stripe.api_key = os.getenv("STRIPE_API_KEY")

payment = APIRouter()

tags_metadata = ["Payment V1"]

collection_loan = db["loans"]
collection_process = db["process"]
collection_payment_type = db["pymentTypes"]

@payment.post("/api/v1/payment/createCheckout", tags = tags_metadata)
async def create_checkout(bodyConfig: dict):
    # Generar 3 Productos en Stripe por cada idPaymentType
    producto_by_payment= collection_payment_type.find_one({"idPaymentType": bodyConfig["idPaymentType"]})
    amount_to_pay = int(bodyConfig["amount"] * 100) 
    price = stripe.Price.create(
        unit_amount=amount_to_pay,
        currency='mxn',
        product=producto_by_payment["idProduct"],
    )

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price': price.id,
            'quantity': 1,
        }],
        locale="es-419",
        mode='payment',
        success_url=f"{os.getenv('FRONT_END_CLIENT_URL')}/pago?result=success",
        cancel_url=f"{os.getenv('FRONT_END_CLIENT_URL')}/pago?result=cancel",
        customer_email=bodyConfig["email"],
        metadata={
            "idSystemUser": bodyConfig["idSystemUser"],
            "idProcesses": bodyConfig["idProcesses"],
            "idLoans": bodyConfig["idLoans"],
            "idLoan": bodyConfig["idLoan"],
            "idPaymentType": bodyConfig["idPaymentType"],
        }
    )

    return {
        "url": session.url,
    }

@payment.post("/api/v1/payment/webhook", tags = tags_metadata)
async def webhook(request: Request, stripe_signature: str = Header(str)):
    format_iso= FormatDate()
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
    data = await request.body()
    event= None

    
    try:
        event = stripe.Webhook.construct_event(
            payload= data, 
            sig_header= stripe_signature, 
            secret= webhook_secret
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except stripe.error.SignatureVerificationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    
    if event.type == 'checkout.session.completed':
        format_iso_cdmx = format_iso.timezone_cdmx()
        session = event.data.object
        metadata = session["metadata"]
        print(metadata)
        id_payment_intent = session["payment_intent"]
        payment_intent = stripe.PaymentIntent.retrieve(id_payment_intent)
        id_payment_method = payment_intent["payment_method"]
        payment_method = stripe.PaymentMethod.retrieve(id_payment_method)

        id_history_payment = generate_UUID()

        query = {"loans.idLoan": metadata["idLoan"]}

        loan_info = collection_loan.find_one({"idLoans": metadata["idLoans"]})
        find_loan_info = {}

        if loan_info:
            for loan in loan_info["loans"]:
                if loan["idLoan"] == metadata["idLoan"]:
                    find_loan_info = loan
                    break

        amount_total = session["amount_total"] / 100;


        new_history_payment = {
            "idHistoryPayment": id_history_payment,
            "amount": amount_total,
            "card": payment_method["card"]["last4"],
            "brand": payment_method["card"]["brand"],
            "paymentFrom": "stripe",
            "paidAt": format_iso_cdmx,
            "dueDateAt": find_loan_info["nextPaymentAt"],
            "idPaymentIntent": id_payment_intent,
            "idPaymentMethod": id_payment_method,
        }

        id_payment_type = int(metadata["idPaymentType"])
        print(id_payment_type)

        next_payment_at = format_iso.add_single_month(find_loan_info["nextPaymentAt"])

        if id_payment_type == 1:
            update = {"$push": {"loans.$.historyPayment": new_history_payment},
                    "$set": {"loans.$.idStatus": 1, "loans.$.nextPaymentAt": next_payment_at}
                    }
            collection_loan.update_one(query, update)
        elif id_payment_type == 2:
            update = {"$push": {"loans.$.historyPayment": new_history_payment},
                    "$set": {"loans.$.idStatus": 5, "loans.$.nextPaymentAt": None, "loans.$.isLiquidated": True, "loans.$.approvedAt": format_iso_cdmx}
                    }
            document_process = collection_process.find_one({"idProcesses": metadata["idProcesses"]})
            amount_available = document_process["amountAvailable"]
            new_amount_available = amount_available + find_loan_info["amountLoan"]
            collection_loan.update_one(query, update)
            collection_process.update_one({"idProcesses": metadata["idProcesses"]}, {"$set": {"amountAvailable": new_amount_available}})
        elif id_payment_type == 3:
            amount_to_capital = amount_total - find_loan_info["amountMonthly"]
            document_process = collection_process.find_one({"idProcesses": metadata["idProcesses"]})
            amount_available = document_process["amountAvailable"] + amount_to_capital
            new_amount_loan = find_loan_info["amountLoan"] - amount_to_capital
            new_amount_interest = new_amount_loan * document_process["interestRate"]
            new_amount_iva = new_amount_interest * document_process["tax"]
            new_amount_monthly = new_amount_interest + new_amount_iva
            new_amount_pay_off = new_amount_monthly + new_amount_loan

            update = {"$push": {"loans.$.historyPayment": new_history_payment},
                    "$set": {
                        "loans.$.idStatus": 1, 
                        "loans.$.nextPaymentAt": next_payment_at, 
                        "loans.$.amountLoan": new_amount_loan, 
                        "loans.$.amountInterest": new_amount_interest,
                        "loans.$.amountIva": new_amount_iva,
                        "loans.$.amountMonthly": new_amount_monthly,
                        "loans.$.amountPayOff": new_amount_pay_off,
                        }
                    }
            collection_loan.update_one(query, update)
            collection_process.update_one({"idProcesses": metadata["idProcesses"]}, {"$set": {"amountAvailable": amount_available}})


    return {"message": "OK"}
