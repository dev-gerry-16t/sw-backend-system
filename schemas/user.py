def userRegisterEntity(id, item) -> dict:
    return {  
            "id": str(id),
            "idSystemUser":item["idSystemUser"],
            "idAddresses":item["idAddresses"],
            "idProcesses":item["idProcesses"],
            "idPersonalDocuments":item["idPersonalDocuments"],
            "idProfile":item["idProfile"],
            "idBankAccounts":item["idBankAccounts"],
            "idUserType":item["idUserType"],
            "screenNumber":item["screenNumber"],
            "idLoans":item["idLoans"],
            "username":item["username"],

    }

def userLoginEntity(item) -> dict:
    return {    
            "email":item["email"],
            "phoneNumber":item["phoneNumber"],
            "idUserType":item["idUserType"],
            "screenNumber":item["screenNumber"],
            "idSystemUser":item["idSystemUser"],
            "idAddresses":item["idAddresses"],
            "idProcesses":item["idProcesses"],
            "idPersonalDocuments":item["idPersonalDocuments"],
            "idProfile":item["idProfile"],
            "idBankAccounts":item["idBankAccounts"],
            "lastLoginAt":item["lastLoginAt"] or "",
            "idLoans":item["idLoans"],
            "token":item["token"],
            "path":item["path"] or "/home",
            "profileInformation":item["profileInformation"],
            "username":item["username"],
            "level":item["level"],
    }