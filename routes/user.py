from fastapi import APIRouter, HTTPException, Query
from config.db import db
from schemas.user import userRegisterEntity, userLoginEntity
from models.user import SetUser, NewUser, ResponseNewUser, ResponseLogin, Login, ResponseProgress
from utils.selectTemplateEmail import select_template_email
from utils.password import password_encrypt, password_verify
from utils.token import create_access_token, verify_token
from utils.generateUUID import generate_UUID
from dotenv import load_dotenv
from pymongo import errors
from utils.formatDate import FormatDate

box = "User Register V1"

collection_process = db["process"]
collection = db["customers"]
collection_profile = db["profiles"]
collection_screen = db["screens"]
collection_config = db["configs"]

user = APIRouter()


@user.post('/api/v1/user/register', response_model=ResponseNewUser, tags=[box])
def user_register(request: NewUser):
    format_iso = FormatDate()

    collection.create_index("email", unique=True)
    collection.create_index("phoneNumber", unique=True)
    new_user = dict(request)
    new_user["password"] = password_encrypt(new_user["password"])
    new_dict = {
        "idSystemUser": generate_UUID(),
        "idAddresses": generate_UUID(),
        "idProcesses": generate_UUID(),
        "idPersonalDocuments": generate_UUID(),
        "idProfile": generate_UUID(),
        "idBankAccounts": generate_UUID(),
        "idLoans": generate_UUID(),
        "registerAt": format_iso.timezone_cdmx(),
        "lastLoginAt": None,
        "username": new_user["username"],
        "level": 1,
    }
    join_dict = {**new_user, **new_dict}

    try:
        id = collection.insert_one(join_dict).inserted_id
        return userRegisterEntity(id, join_dict)
    except errors.DuplicateKeyError as e:
        raise HTTPException(status_code=400, detail={"dbMessage": str(
            e), "errorMessage": "El correo o numero de celular ya esta en uso"})


@user.post('/api/v1/user/login', tags=[box])
def user_login(user: Login):
    format_iso = FormatDate()

    user_form = dict(user)
    user_db = collection.find_one({"email": user_form["email"]})
    if user_db is None:
        raise HTTPException(status_code=400, detail={
                            "dbMessage": "User in db is None", "errorMessage": "Usuario no registrado, favor de registarse antes de iniciar sesión"})

    user_profile = collection_profile.find_one({"idSystemUser": user_db["idSystemUser"]}, {
                                               "_id": 0, "idProfile": 0, "idSystemUser": 0})
    collection.update_one({"_id": user_db["_id"]}, {
                          "$set": {"lastLoginAt": format_iso.timezone_cdmx()}}, upsert=True)

    if not password_verify(user_form["password"], user_db["password"]):
        raise HTTPException(status_code=401, detail={
                            "dbMessage": "", "errorMessage": "Verifique su correo o contraseña"})

    token = create_access_token(user_form["email"])
    path_user = collection_screen.find_one(
        {"screenNumber": user_db["screenNumber"]})
    join_dict = {**user_db, "token": token,
                 "path": path_user["path"], "profileInformation": user_profile["profileInformation"] if user_profile is not None else {}}
    
    return userLoginEntity(join_dict)


@user.get('/api/v1/user/getLogin/{idSystemUser}', tags=[box])
def user_get_login(idSystemUser: str):
    id_system_user = idSystemUser
    format_iso = FormatDate()

    user_db = collection.find_one({"idSystemUser": id_system_user})
    user_profile = collection_profile.find_one({"idSystemUser": id_system_user}, {
                                               "_id": 0, "idProfile": 0, "idSystemUser": 0})

    collection.update_one({"_id": user_db["_id"]}, {
                          "$set": {"lastLoginAt": format_iso.timezone_cdmx()}}, upsert=True)

    token = create_access_token(user_db["email"])
    path_user = collection_screen.find_one(
        {"screenNumber": user_db["screenNumber"]})

    join_dict = {**user_db, "token": token,
                 "path": path_user["path"], "profileInformation": user_profile["profileInformation"]}

    return userLoginEntity(join_dict)


@user.get('/api/v1/user/progress/{idSystemUser}', response_model=ResponseProgress, tags=[box])
def user_progress(idSystemUser: str, screen: str = Query(None)):
    int_screen_number = int(screen)

    list_screen = list(collection_screen.find({}))
    next_screen_number = int_screen_number + 1

    for screen in list_screen:
        if screen["screenNumber"] == next_screen_number:
            collection.update_one({"idSystemUser": idSystemUser}, {
                                  "$set": {"screenNumber": screen["screenNumber"]}}, upsert=True)
            return {"nextScreen": screen["screenNumber"]}


@user.post('/api/v1/user/recoveryPassword', tags=[box])
def user_recovery_password(recovery: dict):
    user_form = dict(recovery)

    if user_form["email"] is None or user_form["email"] == "":
        raise HTTPException(status_code=400, detail={
                            "dbMessage": "User in db is None", "errorMessage": "El correo es requerido"})

    user_db = collection.find_one({"email": user_form["email"]})

    if user_db is None:
        raise HTTPException(status_code=400, detail={
                            "dbMessage": "User in db is None", "errorMessage": "Usuario no registrado, favor de registarse antes de iniciar sesión"})

    token = create_access_token(user_db["idSystemUser"], 5)

    email_to = user_db["email"]
    profile_name = user_db["username"]

    select_template_email(
        id_template=6,
        email_to=email_to,
        user=profile_name,
        token=token
    )

    return {"message": "Se ha enviado un correo para recuperar tu contraseña"}


@user.post('/api/v1/user/changePassword', tags=[box])
def user_change_password(change: dict):
    user_form = dict(change)
    token = user_form["token"]
    password = user_form["password"]

    payload = verify_token(token)

    if payload:
        collection.update_one({"idSystemUser": payload["sub"]}, {
                              "$set": {"password": password_encrypt(password)}}, upsert=True)
        return {"message": "Se ha cambiado la contraseña"}

    else:
        raise HTTPException(status_code=400, detail={
                            "dbMessage": "Token is not valid", "errorMessage": "Token invalido o expirado"})


@user.put('/api/v1/user/changeLevel/{idSystemUser}', tags=[box])
def user_change_level(idSystemUser: str, level: int = Query(None)):
    collection.update_one({"idSystemUser": idSystemUser}, {"$set": {"level": level}}, upsert=True)

    configs_rule = collection_config.find_one({})
    config_level = configs_rule["configLevel"]
    interest_by_level = 0

    for levelItem in config_level:
            if level == levelItem["level"]:
                interest_by_level = levelItem["interest"]
                break

    collection_process.update_one(
        {"idSystemUser": idSystemUser},
        {"$set": {"interestRate": interest_by_level}})
    
    return {"message": "Se ha cambiado el nivel"}

    #  collection.update_one({"idSystemUser": idSystemUser}, {"$set": {"screenNumber": int_screen_number}}, upsert=True)


# @app.get("/protected_route1")
# async def protected_route1(current_user: str = Depends(authenticate_user)):
#     return {"message": "Ruta protegida 1"}
