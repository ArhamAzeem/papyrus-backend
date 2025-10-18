from passlib.context import CryptContext
from jose import jwt,JWTError
from datetime import datetime, timedelta
from app.core.config import Setting

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, password):
    return pwd_context.verify(plain_password, password)

def create_access_token(data: dict,expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=Setting.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp":expire})
    return jwt.encode(to_encode, Setting.SECRET_KEY,algorithm=Setting.ALGORITHM)