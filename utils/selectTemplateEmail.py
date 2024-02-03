import requests
import os
import json
import base64
from utils.email import Email
from dotenv import load_dotenv
from utils.slackWebhook import send_slack_message

load_dotenv()

url_domain = os.getenv("FRONT_END_ADMIN_URL")
url_domain_client = os.getenv("FRONT_END_CLIENT_URL")
api_key_mandrill = os.getenv("API_KEY_MANDRILL")
email_notify_admin = os.getenv("EMAIL_NOTIFY_ADMIN")


def send_email_template(template_name, email_to, template_data):
    url = "https://mandrillapp.com/api/1.0/messages/send-template"

    headers = {
        "Content-Type": "application/json"
    }

    result = []
    for key, value in template_data.items():
        result.append({
            "name": key,
            "content": value
        })

    emails_str = email_to
    emails_list = emails_str.split(',')
    result_email = []
    for email in emails_list:
        result_email.append({
            "email": email
        })

    data = {
        "key": api_key_mandrill,
        "template_name": template_name,
        "template_content": [],
        "message": {
            "from_email": "no-reply@swip.mx",
            "from_name": "Swip",
            "to": result_email,
            "merge_language": "handlebars",
            "global_merge_vars": result,
        }
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        print('Correo electrónico enviado exitosamente.')
    else:
        print('Hubo un problema al enviar el correo electrónico.')


def select_template_email(id_template, **options):
    email_to_admins = email_notify_admin

    if id_template == 1:
        template_name = "SW_REQUESTCREDIT_V1"
        id_processes = options.get("id_processes", None)

        if id_processes is not None:
            send_email_template(
                template_name=template_name,
                email_to=email_to_admins,
                template_data={"host": url_domain, "idProcesses": id_processes}
            )
            send_slack_message(
                f"Se ha solicitado un nuevo crédito, entra a {url_domain}/procesos/detalle/{id_processes} y valida la información para pre aprobar")

    elif id_template == 2:
        template_name = "SW_APPROVEDCREDIT_V2"
        email_to = options.get("email_to", None)
        user = options.get("user", None)
        amount_approved = options.get("amount_approved", None)

        if email_to is not None and user is not None and amount_approved is not None:
            send_email_template(
                template_name=template_name,
                email_to=email_to,
                template_data={"user": user,
                               "amountApprovedCredit": amount_approved}
            )
    elif id_template == 3:
        template_name = "SW_REJECTEDCREDIT_V1"
        email_to = options.get("email_to", None)
        user = options.get("user", None)

        if email_to is not None and user is not None:
            send_email_template(
                template_name=template_name,
                email_to=email_to,
                template_data={"user": user}
            )
    elif id_template == 4:
        template_name = "SW_REQUESTLOAN_V1"
        email_to = email_to_admins
        id_processes = options.get("id_processes", None)

        if email_to is not None and id_processes is not None:
            send_email_template(
                template_name=template_name,
                email_to=email_to,
                template_data={"host": url_domain, "idProcesses": id_processes}
            )
            send_slack_message(
                f"Se ha solicitado un nuevo prestamo, entra a {url_domain}/procesos/detalle/{id_processes} y dispersa el dinero")
    elif id_template == 6:
        template_name = "SW_RECOVERYPASS_V1"
        email_to = options.get("email_to", None)
        user = options.get("user", None)
        token = options.get("token", None)

        if email_to is not None and user is not None and token is not None:
            send_email_template(
                template_name=template_name,
                email_to=email_to,
                template_data={"user": user, "host": url_domain_client,
                               "token": token}
            )
    elif id_template == 7:
        template_name = "SW_PREAPPROVECREDIT_V1"
        email_to = options.get("email_to", None)
        user = options.get("user", None)
        amount_approved = options.get("amount_approved", None)
        id_system_user = options.get("id_system_user", None)
        data_user = {"idSystemUser": id_system_user}
        data_user_jumps = json.dumps(data_user)
        id_encoded = base64.b64encode(data_user_jumps.encode()).decode()

        if email_to is not None and user is not None and amount_approved is not None and id_system_user is not None:
            send_email_template(
                template_name=template_name,
                email_to=email_to,
                template_data={"user": user, "amountApprovedCredit": amount_approved,
                               "host": url_domain_client, "token": id_encoded}
            )
    elif id_template == 8:
        template_name = "SW_CONFIRMFIRSTSCHEDULE_V1"
        email_to = email_to_admins
        appointment_date = options.get("appointment_date", None)
        id_processes = options.get("id_processes", None)
        user = options.get("user", None)

        if email_to is not None and user is not None and appointment_date is not None and id_processes is not None:
            send_email_template(
                template_name=template_name,
                email_to=email_to,
                template_data={"host": url_domain, "idProcesses":  id_processes,
                               "appointmentDate": appointment_date, "user": user}
            )
            send_slack_message(
                f"Se ha solicitado programado una cita con el usuario {user} para el {appointment_date}, aqui dejo el detalle {url_domain}/procesos/detalle/{id_processes}")
    elif id_template == 9:
        template_name = "SW_CONFIRMFIRSTSCHEDULE_USER_V1"
        email_to = options.get("email_to", None)
        appointment_date = options.get("appointment_date", None)
        user = options.get("user", None)

        if email_to is not None and user is not None and appointment_date is not None:
            send_email_template(
                template_name=template_name,
                email_to=email_to,
                template_data={
                    "appointmentDate": appointment_date, "user": user}
            )
    elif id_template == 11:
        template_name = "SW_LOANSENT_V1"
        email_to = options.get("email_to", None)
        amount_loan = options.get("amount_loan", None)
        user = options.get("user", None)

        if email_to is not None and user is not None and amount_loan is not None:
            send_email_template(
                template_name=template_name,
                email_to=email_to,
                template_data={"amountLoan": amount_loan, "user": user}
            )
            
    elif id_template == 13:
        template_name = "SW_WELCOMELEAD_WITHAMOUNT_V1"
        email_to = options.get("email_to", None)
        user = options.get("user", None)
        year = options.get("year", None)
        brand = options.get("brand", None)
        model = options.get("model", None)
        version = options.get("version", None)
        amount = options.get("amount", None)

        if email_to is not None and user is not None and year is not None and brand is not None and model is not None and version is not None and amount is not None:
            send_email_template(
                template_name=template_name,
                email_to=email_to,
                template_data={"firstname": user, "year": year, "brand": brand, "model": model, "version": version, "swipBuyPrice": amount}
            )

# def select_template_email(id_template, **options):

#     email = Email()
#     email_from = "Swip <no-reply@info.swip.mx>"
#     email_to_admins = "gerardocto@swip.mx"

#     if id_template == 1:
#         template_name="SW_REQUESTCREDIT_V1"
#         id_processes = options.get("id_processes", None)

#         if  id_processes is not None:
#             email.send_email_template(
#                 template_name = template_name,
#                 email_to = email_to_admins,
#                 email_from = email_from,
#                 template_data = { "url": f"{url_domain}/procesos/detalle/{id_processes}" }
#             )
#     elif id_template == 2:
#         template_name="SW_APPROVEDCREDIT_V2"
#         email_to = options.get("email_to", None)
#         user = options.get("user", None)
#         amount_approved = options.get("amount_approved", None)

#         if email_to is not None and user is not None and amount_approved is not None:
#             email.send_email_template(
#                 template_name = template_name,
#                 email_to = email_to,
#                 email_from = email_from,
#                 template_data = { "user": user, "amountApprovedCredit": amount_approved }
#             )
#     elif id_template == 3:
#         template_name="SW_REJECTEDCREDIT_V1"
#         email_to = options.get("email_to", None)
#         user = options.get("user", None)

#         if email_to is not None and user is not None:
#             email.send_email_template(
#                 template_name = template_name,
#                 email_to = email_to,
#                 email_from = email_from,
#                 template_data = { "user": user }
#             )
#     elif id_template == 4:
#         template_name="SW_REQUESTLOAN_V1"
#         email_to = email_to_admins
#         id_processes = options.get("id_processes", None)

#         if email_to is not None and id_processes is not None:
#             email.send_email_template(
#                 template_name = template_name,
#                 email_to = email_to,
#                 email_from = email_from,
#                 template_data = { "url": f"{url_domain}/procesos/detalle/{id_processes}" }
#             )
#     elif id_template == 7:
#         template_name="SW_PREAPPROVECREDIT_V1"
#         email_to = options.get("email_to", None)
#         user = options.get("user", None)
#         amount_approved = options.get("amount_approved", None)
#         id_system_user = options.get("id_system_user", None)
#         data_user = { "idSystemUser": id_system_user }
#         data_user_jumps = json.dumps(data_user)
#         id_encoded = base64.b64encode(data_user_jumps.encode()).decode()

#         if email_to is not None and user is not None and amount_approved is not None and id_system_user is not None:
#             email.send_email_template(
#                 template_name = template_name,
#                 email_to = email_to,
#                 email_from = email_from,
#                 template_data = { "user": user, "amountApprovedCredit": amount_approved, "url":  f"{url_domain_client}/programar-cita?d={id_encoded}" }
#             )
#     elif id_template == 8:
#         template_name="SW_CONFIRMFIRSTSCHEDULE_V1"
#         email_to = email_to_admins
#         appointment_date = options.get("appointment_date", None)
#         id_processes = options.get("id_processes", None)
#         user = options.get("user", None)

#         if email_to is not None and user is not None and appointment_date is not None and id_processes is not None:
#             email.send_email_template(
#                 template_name = template_name,
#                 email_to = email_to,
#                 email_from = email_from,
#                 template_data = { "url": f"{url_domain}/procesos/detalle/{id_processes}", "appointmentDate": appointment_date, "user": user }
#             )
#     elif id_template == 9:
#         template_name="SW_CONFIRMFIRSTSCHEDULE_USER_V1"
#         email_to = options.get("email_to", None)
#         appointment_date = options.get("appointment_date", None)
#         user = options.get("user", None)

#         if email_to is not None and user is not None and appointment_date is not None:
#             email.send_email_template(
#                 template_name = template_name,
#                 email_to = email_to,
#                 email_from = email_from,
#                 template_data = { "appointmentDate": appointment_date, "user": user }
#             )
#     elif id_template == 11:
#         template_name="SW_LOANSENT_V1"
#         email_to = options.get("email_to", None)
#         amount_loan = options.get("amount_loan", None)
#         user = options.get("user", None)

#         if email_to is not None and user is not None and amount_loan is not None:
#             email.send_email_template(
#                 template_name = template_name,
#                 email_to = email_to,
#                 email_from = email_from,
#                 template_data = { "amountLoan": amount_loan, "user": user }
#             )


# 1	SW_REQUESTCREDIT_V1
# 2	SW_APPROVEDCREDIT_V2
# 3	SW_REJECTEDCREDIT_V1
# 4	SW_REQUESTLOAN_V1
# 5	SW_VERIFYEMAIL_V1
# 6	SW_RECOVERYPASS_V1
# 7	SW_PREAPPROVECREDIT_V1
# 8	SW_CONFIRMFIRSTSCHEDULE_V1
# 9 SW_CONFIRMFIRSTSCHEDULE_USER_V1
# 10	SW_PAYMENTREMINDER_V1
