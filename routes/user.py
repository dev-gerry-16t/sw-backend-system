from datetime import datetime
from fastapi import APIRouter, HTTPException, Query
from config.db import db
from schemas.user import userRegisterEntity, userLoginEntity
from models.user import SetUser, NewUser, ResponseNewUser, ResponseLogin, Login, ResponseProgress
from utils.password import password_encrypt, password_verify
from utils.token import create_access_token
from utils.generateUUID import generate_UUID
from dotenv import load_dotenv
from pymongo import errors

box = "User Register V1"


collection = db["user"]
collection_screen = db["screen"]

user = APIRouter()


@user.post('/api/v1/user/register',response_model=ResponseNewUser,tags=[box])
def user_register(user: NewUser):
    timestamp = datetime.now()
    timestamp_formatted = timestamp.strftime("%Y-%m-%d %H:%M:%S")

    collection.create_index("email", unique=True)
    collection.create_index("phoneNumber", unique=True)
    new_user = dict(user)
    new_user["password"] = password_encrypt(new_user["password"])
    new_dict = {
        "idSystemUser": generate_UUID(),
        "idAddresses": generate_UUID(),
        "idProcesses": generate_UUID(),
        "idPersonalDocuments": generate_UUID(),
        "idProfile": generate_UUID(),
        "idBankAccounts": generate_UUID(),
        "idCarDocuments": generate_UUID(),
        "idLoans": generate_UUID(),
        "registerAt": timestamp_formatted
    }
    join_dict = {**new_user,**new_dict}

    try:
        id= collection.insert_one(join_dict).inserted_id
        return userRegisterEntity(id, join_dict)
    except errors.DuplicateKeyError as e:
        raise HTTPException(status_code=400, detail={"dbMessage":str(e),"errorMessage":"El correo o numero de celular ya esta en uso"})

@user.post('/api/v1/user/login',response_model=ResponseLogin,tags=[box])
def user_login(user: Login):
    timestamp = datetime.now()
    timestamp_formatted = timestamp.strftime("%Y-%m-%d %H:%M:%S")

    user_form = dict(user)
    user_db= collection.find_one({"email": user_form["email"]})
    collection.update_one({"_id": user_db["_id"]}, {"$set": {"lastLoginAt": timestamp_formatted}}, upsert=True)
    
    if not password_verify(user_form["password"], user_db["password"]):
        raise HTTPException(status_code=401, detail={"dbMessage":"","errorMessage":"Verifique su correo o contraseña"})
    
    token = create_access_token(user_form["email"])
    path_user = collection_screen.find_one({"screenNumber": user_db["screenNumber"]})

    join_dict = {**user_db, "token": token,"path": path_user["path"]}   
    return  userLoginEntity(join_dict)

@user.get('/api/v1/user/progress/{idSystemUser}',response_model=ResponseProgress,tags=[box])
def user_progress(idSystemUser: str, screen:str = Query(None) ):
     int_screen_number= int(screen)

     list_screen= list(collection_screen.find({}))

     for screen in list_screen:
         print(screen)
         if screen["screenNumber"] == int_screen_number:
                int_index= screen["index"] + 1
                next_screen_dict= collection_screen.find_one({"index": int_index})
                collection.update_one({"idSystemUser": idSystemUser}, {"$set": {"screenNumber": next_screen_dict["screenNumber"]}}, upsert=True)
                return  {"nextScreen": next_screen_dict["screenNumber"]}

    #  collection.update_one({"idSystemUser": idSystemUser}, {"$set": {"screenNumber": int_screen_number}}, upsert=True)
    
  

# @app.get("/protected_route1")
# async def protected_route1(current_user: str = Depends(authenticate_user)):
#     return {"message": "Ruta protegida 1"}