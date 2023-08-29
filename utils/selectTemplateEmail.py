import os
import json
import base64
from utils.email import Email
from dotenv import load_dotenv

load_dotenv()

url_domain = os.getenv("FRONT_END_ADMIN_URL")
url_domain_client = os.getenv("FRONT_END_CLIENT_URL")

def select_template_email(id_template, **options):
    
    email = Email()
    email_from = "Swip <no-reply@info.swip.mx>"
    email_to_admins = "gerardocto@swip.mx"

    if id_template == 1:
        template_name="SW_REQUESTCREDIT_V1"
        id_processes = options.get("id_processes", None)

        if  id_processes is not None:
            email.send_email_template(
                template_name = template_name,
                email_to = email_to_admins,
                email_from = email_from,
                template_data = { "url": f"{url_domain}/procesos/detalle/{id_processes}" }
            )            
    elif id_template == 2:
        template_name="SW_APPROVEDCREDIT_V2"
        email_to = options.get("email_to", None)
        user = options.get("user", None)
        amount_approved = options.get("amount_approved", None)

        if email_to is not None and user is not None and amount_approved is not None:
            email.send_email_template(
                template_name = template_name,
                email_to = email_to,
                email_from = email_from,
                template_data = { "user": user, "amountApprovedCredit": amount_approved }
            )
    elif id_template == 3:
        template_name="SW_REJECTEDCREDIT_V1"
        email_to = options.get("email_to", None)
        user = options.get("user", None)

        if email_to is not None and user is not None:
            email.send_email_template(
                template_name = template_name,
                email_to = email_to,
                email_from = email_from,
                template_data = { "user": user }
            )
    elif id_template == 4:
        template_name="SW_REQUESTLOAN_V1"
        email_to = email_to_admins
        id_processes = options.get("id_processes", None)

        if email_to is not None and id_processes is not None:
            email.send_email_template(
                template_name = template_name,
                email_to = email_to,
                email_from = email_from,
                template_data = { "url": f"{url_domain}/procesos/detalle/{id_processes}" }
            )
    elif id_template == 7:
        template_name="SW_PREAPPROVECREDIT_V1"
        email_to = options.get("email_to", None)
        user = options.get("user", None)
        amount_approved = options.get("amount_approved", None)
        id_system_user = options.get("id_system_user", None)
        data_user = { "idSystemUser": id_system_user }
        data_user_jumps = json.dumps(data_user)
        id_encoded = base64.b64encode(data_user_jumps.encode()).decode()

        if email_to is not None and user is not None and amount_approved is not None and id_system_user is not None:
            email.send_email_template(
                template_name = template_name,
                email_to = email_to,
                email_from = email_from,
                template_data = { "user": user, "amountApprovedCredit": amount_approved, "url":  f"{url_domain_client}/programar-cita?d={id_encoded}" }
            )
    elif id_template == 8:
        template_name="SW_CONFIRMFIRSTSCHEDULE_V1"
        email_to = email_to_admins
        appointment_date = options.get("appointment_date", None)
        id_processes = options.get("id_processes", None)
        user = options.get("user", None)

        if email_to is not None and user is not None and appointment_date is not None and id_processes is not None:
            email.send_email_template(
                template_name = template_name,
                email_to = email_to,
                email_from = email_from,
                template_data = { "url": f"{url_domain}/procesos/detalle/{id_processes}", "appointmentDate": appointment_date, "user": user }
            )
    elif id_template == 9:
        template_name="SW_CONFIRMFIRSTSCHEDULE_USER_V1"
        email_to = options.get("email_to", None)
        appointment_date = options.get("appointment_date", None)
        user = options.get("user", None)

        if email_to is not None and user is not None and appointment_date is not None:
            email.send_email_template(
                template_name = template_name,
                email_to = email_to,
                email_from = email_from,
                template_data = { "appointmentDate": appointment_date, "user": user }
            )
    elif id_template == 11:
        template_name="SW_LOANSENT_V1"
        email_to = options.get("email_to", None)
        amount_loan = options.get("amount_loan", None)
        user = options.get("user", None)

        if email_to is not None and user is not None and amount_loan is not None:
            email.send_email_template(
                template_name = template_name,
                email_to = email_to,
                email_from = email_from,
                template_data = { "amountLoan": amount_loan, "user": user }
            )



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