# app/core/middleware/admin_middleware.py
from fastapi import Request
from fastapi.responses import JSONResponse
from jose import jwt, JWTError
from app.db.session import SessionLocal
from app.models.admin_model import Admin
from app.models.token_blacklist_model import BlacklistedToken
from app.core.config import Setting

EXCLUDED_ADMIN_PATHS = [
    "/api/v1/admin/auth/login",
    "/api/v1/admin/auth/register",
    "/docs",
    "/openapi.json",
    "/redoc",
]

async def admin_auth_middleware(request: Request, call_next):
    # Only run middleware for admin routes
    if not request.url.path.startswith("/api/v1/admin") or request.url.path in EXCLUDED_ADMIN_PATHS:
        return await call_next(request)

    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return JSONResponse(
            status_code=401,
            content={"success": False, "message": "Authorization header missing or invalid", "data": {}}
        )

    token = auth_header.split(" ")[1]
    db = SessionLocal()
    try:
        if db.query(BlacklistedToken).filter(BlacklistedToken.token == token).first():
            return JSONResponse(
                status_code=401,
                content={"success": False, "message": "Token has been revoked", "data": {}}
            )

        payload = jwt.decode(token, Setting.SECRET_KEY, algorithms=[Setting.ALGORITHM])
        email = payload.get("sub")
        if not email:
            return JSONResponse(
                status_code=401,
                content={"success": False, "message": "Invalid token payload", "data": {}}
            )

        # Get admin from DB
        admin = db.query(Admin).filter(Admin.email == email).first()
        if not admin:
            return JSONResponse(
                status_code=401,
                content={"success": False, "message": "Admin not found", "data": {}}
            )

        request.state.admin = admin
        response = await call_next(request)
        return response

    except JWTError:
        return JSONResponse(
            status_code=401,
            content={"success": False, "message": "Invalid or expired token", "data": {}}
        )
    finally:
        db.close()