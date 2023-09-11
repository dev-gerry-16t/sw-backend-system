import os
import time
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("TOKEN_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

def create_access_token(username: str, minutes=360):
    expires = datetime.utcnow() + timedelta(minutes=minutes)
    to_encode = {"sub": username, "exp": expires}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        fecha_vencimiento = payload["exp"]
        fecha_actual = int(time.time())

        if fecha_vencimiento > fecha_actual:
            return payload
        else:
            return None
    except JWTError:
        return None


def authenticate_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Token inválido")
        # Aquí puedes agregar lógica adicional, como verificar en una base de datos si el usuario existe o tiene los permisos adecuados
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")
