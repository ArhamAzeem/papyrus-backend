from fastapi import Depends, HTTPException, Request, status
from jose import JWTError, jwt
from app.core.config import Setting
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user_model import User
from app.models.token_blacklist_model import BlacklistedToken
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": False,
                "message": "Missing authentication token",
                "data": {}
            }
        )

    try:
        payload = jwt.decode(token, Setting.SECRET_KEY, algorithms=[Setting.ALGORITHM])
        email: str = payload.get("sub")

        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "success": False,
                    "message": "Invalid token",
                    "data": {}
                }
            )

        # Check if token is blacklisted
        if db.query(BlacklistedToken).filter(BlacklistedToken.token == token).first():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "success": False,
                    "message": "Token revoked",
                    "data": {}
                }
            )

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": False,
                "message": "Invalid token",
                "data": {}
            }
        )

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "message": "User not found",
                "data": {}
            }
        )

    return user

async def get_current_admin(request: Request):
    admin = getattr(request.state, "admin", None)
    if not admin:
        raise HTTPException(status_code=401, detail={"success": False, "message": "Admin not authenticated", "data": {}})
    return admin