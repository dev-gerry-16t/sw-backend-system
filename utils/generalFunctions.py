from utils.generateUUID import generate_UUID

def generate_invoice_number(name, id_system):
    id_invoice = generate_UUID()

    parts = id_system.split("-")
    parts_invoice = id_invoice.split("-")

    invoice_number = name + "-" + parts[0] + "-" + parts_invoice[0]

    return invoice_number
