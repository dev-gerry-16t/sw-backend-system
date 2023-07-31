def carInfoResponseEntity(**items)-> dict:
    return {
        "idCarInformation":items["id_car"],
        "idSystemUser":items["id_system_user"],
    }

def setCarInfoEntity(id, items)-> dict:
    return {
        "idCarInformation":id,
        "idSystemUser":items["idSystemUser"],
        "information":{
            "brand":items["brand"],
            "model":items["model"],
            "type":items["type"],
            "transmissionType":items["transmissionType"],
            "color":items["color"],
            "year":items["year"],
            "mileage":items["mileage"],
            "amountPrice":items["amountPrice"],
            "numberPlates":items["numberPlates"],
            "isInsured":items["isInsured"],
            "amountAppraise":0,
            "amountInsured": 0,
        }
    }