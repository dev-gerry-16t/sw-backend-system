def discount_deprecation(price, discount):
    parse_price_to_int = float(price)
    return parse_price_to_int * (1 - discount)

def charge_appreciation(price, charge):
    parse_price_to_int = float(price)
    return parse_price_to_int * (1 + charge)
