def generate_invoice_number(id_system, id_third_party_service):
    parts = id_system.split("-")
    invoice_number = "PRESW" + "-" + parts[0] + "-" + id_third_party_service

    return invoice_number