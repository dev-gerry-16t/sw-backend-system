from passlib.hash import sha256_crypt

def password_encrypt(password: str ) -> str:
    return sha256_crypt.encrypt(password)

def password_verify(plain_password: str, hashed_password: str) -> bool:
    return sha256_crypt.verify(plain_password, hashed_password)
