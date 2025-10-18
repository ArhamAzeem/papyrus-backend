from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.token_blacklist_model import BlacklistedToken
from app.models.user_model import User
from app.core.deps import get_db, get_current_user
from app.schemas.user_schema import UserRegister, UserLogin, ForgotPassword, ResetPassword
from app.core.security import get_password_hash, verify_password, create_access_token
from app.services.email_service import send_verification_email, send_reset_email
import os
import uuid
from app.utils.response import success_response, error_message
from fastapi.security import OAuth2PasswordBearer

router = APIRouter(prefix="/auth", tags=["Auth"])
UPLOAD_DIR = "uploads/profile_images"
os.makedirs(UPLOAD_DIR, exist_ok=True)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


@router.post("/register")
async def register(user: UserRegister, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user.email).first():
        return error_message(400, "Email already registered")

    token = str(uuid.uuid4())
    new_user = User(
        full_name=user.full_name,
        email=user.email,
        password=get_password_hash(user.password),
        verification_token=token
    )
    db.add(new_user)
    db.commit()
    await send_verification_email(user.email, token)
    return success_response("Verification Mail Sent Successfully")


@router.get("/verify")
def verify_account(token: str, db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.verification_token == token).first()
        if not user:
            return error_message(400, "Invalid token")

        user.is_verified = True
        user.verification_token = None
        db.commit()
        return success_response("Account verified successfully")
    except Exception as e:
        return error_message(500, str(e))


@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    try:
        db_user = db.query(User).filter(User.email == user.email).first()
        if not db_user or not verify_password(user.password, db_user.password):
            return error_message(400, "Invalid credentials")
        if not db_user.is_verified:
            return error_message(400, "Please verify your email first")

        token = create_access_token({"sub": db_user.email})
        return success_response("Login Successful", {"access_token": token, "token_type": "bearer"})
    except Exception as e:
        return error_message(500, str(e))


@router.post("/logout")
def logout(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    try:
        blacklisted = BlacklistedToken(token=token)
        db.add(blacklisted)
        db.commit()
        return success_response("Logged out successfully")
    except Exception as e:
        return error_message(500, str(e))


@router.post("/forgot-password")
async def forgot_password(data: ForgotPassword, db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.email == data.email).first()
        if not user:
            return error_message(404, "Email not found")

        token = str(uuid.uuid4())
        user.reset_token = token
        db.commit()
        await send_reset_email(user.email, token)
        return success_response("Password reset link sent")
    except Exception as e:
        return error_message(500, str(e))


@router.post("/reset-password")
def reset_password(data: ResetPassword, db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.reset_token == data.token).first()
        if not user:
            return error_message(400, "Invalid token")

        user.password = get_password_hash(data.new_password)
        user.reset_token = None
        db.commit()
        return success_response("Password reset successfully")
    except Exception as e:
        return error_message(500, str(e))


@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    try:
        data = {
            "id": current_user.id,
            "full_name": current_user.full_name,
            "image": current_user.image,
            "is_verified": current_user.is_verified,
            "email": current_user.email
        }
        return success_response("User profile fetched successfully", data)
    except Exception as e:
        return error_message(500, str(e))


@router.put("/profile")
def update_profile(
    full_name: str = Form(...),
    file: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        user_in_db = db.merge(current_user)

        if file:
            file_ext = os.path.splitext(file.filename)[1]
            file_name = f"{uuid.uuid4()}{file_ext}"
            file_path = os.path.join(UPLOAD_DIR, file_name).replace("\\", "/")
            with open(file_path, "wb") as buffer:
                buffer.write(file.file.read())
            user_in_db.image = f"/{file_path}"

        user_in_db.full_name = full_name
        db.commit()
        db.refresh(user_in_db)
        return success_response("User profile updated successfully", {
            "id": user_in_db.id,
            "full_name": user_in_db.full_name,
            "email": user_in_db.email,
            "image": user_in_db.image
        })
    except Exception as e:
        return error_message(500, str(e))