from datetime import datetime, timedelta
from fastapi import  Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import  JWTError, jwt

SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

def create_access_token(username: str):
    expires = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": username, "exp": expires}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

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