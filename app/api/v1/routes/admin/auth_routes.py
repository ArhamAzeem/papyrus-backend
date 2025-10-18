from fastapi import APIRouter, Depends, Form, UploadFile, File
from sqlalchemy.orm import Session
from app.models.admin_model import Admin
from app.models.token_blacklist_model import BlacklistedToken
from app.schemas.admin_schema import AdminLogin, AdminResponse
from app.core.security import get_password_hash, verify_password, create_access_token
from app.utils.response import success_response, error_message
from fastapi.security import OAuth2PasswordBearer
from app.core.deps import get_db
import uuid, os
from jose import JWTError,jwt
from app.core.config import Setting

router = APIRouter(prefix="/admin/auth", tags=["Admin Auth"])
UPLOAD_DIR = "uploads/admin_profile_images"
os.makedirs(UPLOAD_DIR, exist_ok=True)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/admin/auth/login")

@router.post("/login")
def admin_login(admin: AdminLogin, db: Session = Depends(get_db)):
    try:
        db_admin = db.query(Admin).filter(Admin.email == admin.email).first()
        if not db_admin or not verify_password(admin.password, db_admin.password):
            return error_message(400, "Invalid credentials")
        token = create_access_token({"sub": db_admin.email})
        return success_response("Login successful", {"access_token": token, "token_type": "bearer"})
    except Exception as e:
        return error_message(500, str(e))


@router.post("/logout")
def admin_logout(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        blacklisted = BlacklistedToken(token=token)
        db.add(blacklisted)
        db.commit()
        return success_response("Logged out successfully")
    except Exception as e:
        return error_message(500, str(e))


@router.get("/me")
def admin_me(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, Setting.SECRET_KEY, algorithms=[Setting.ALGORITHM])
        email = payload.get("sub")
        admin = db.query(Admin).filter(Admin.email == email).first()
        if not admin:
            return error_message(404, "Admin not found")
        data = {"id": admin.id, "full_name": admin.full_name, "email": admin.email}
        return success_response("Admin profile fetched successfully", data)
    except Exception as e:
        return error_message(500, str(e))
