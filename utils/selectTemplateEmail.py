from utils.email import Email

def select_template_email(id_template, **options):
    email = Email()
    email_from = "Swip <no-reply@info.swip.mx>"
    email_to_admins = "gerardocto@swip.mx"

    if id_template == 1:
        template_name="SW_REQUESTCREDIT_V1"
        id_processes = options.get("idProcesses", None)

        if  id_processes is not None:
            email.send_email_template(
                template_name = template_name,
                email_to = email_to_admins,
                email_from = email_from,
                template_data = { "idProcesses": id_processes }
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
        email_to = options.get("email_to", None)
        id_processes = options.get("idProcesses", None)

        if email_to is not None and id_processes is not None:
            email.send_email_template(
                template_name = template_name,
                email_to = email_to,
                email_from = email_from,
                template_data = { "idProcesses": id_processes }
            )
    elif id_template == 7:
        template_name="SW_PREAPPROVECREDIT_V1"
        email_to = options.get("email_to", None)
        user = options.get("user", None)
        amount_approved = options.get("amount_approved", None)
        url = options.get("url", None)

        if email_to is not None and user is not None and amount_approved is not None and url is not None:
            email.send_email_template(
                template_name = template_name,
                email_to = email_to,
                email_from = email_from,
                template_data = { "user": user, "amountApprovedCredit": amount_approved, "url": url }
            )



# 1	SW_REQUESTCREDIT_V1
# 2	SW_APPROVEDCREDIT_V2
# 3	SW_REJECTEDCREDIT_V1
# 4	SW_REQUESTLOAN_V1
# 5	SW_VERIFYEMAIL_V1
# 6	SW_RECOVERYPASS_V1
# 7	SW_PREAPPROVECREDIT_V1
# 8	SW_CONFIRMFIRSTSCHEDULE_V1
# 9	SW_PAYMENTREMINDER_V1