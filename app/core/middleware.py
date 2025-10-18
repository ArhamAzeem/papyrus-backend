from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from jose import jwt, JWTError
from app.core.config import Setting
from app.db.session import SessionLocal
from app.models.token_blacklist_model import BlacklistedToken
from app.models.user_model import User

bearer_scheme = HTTPBearer()

EXCLUDED_PATHS = [
    "/",
    "/api/v1/auth/login",
    "/api/v1/auth/register",
    "/api/v1/auth/verify",
    "/api/v1/auth/forgot-password",
    "/api/v1/auth/reset-password",
    "/docs",
    "/openapi.json",
    "/redoc",
]

async def auth_middleware(request: Request, call_next):
    if any(request.url.path.startswith(path) for path in EXCLUDED_PATHS):
        return await call_next(request)

    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return JSONResponse(
            status_code=401,
            content={
                "success": False,
                "message": "Authorization header missing or invalid",
                "data": {}
            },
        )
    token = auth_header.split(" ")[1]

    db = SessionLocal()
    try:
        if db.query(BlacklistedToken).filter(BlacklistedToken.token == token).first():
            return JSONResponse(status_code=401, content={"detail": "Token has been revoked"})

        payload = jwt.decode(token, Setting.SECRET_KEY, algorithms=[Setting.ALGORITHM])
        email = payload.get("sub")

        if not email:
            return JSONResponse(
                status_code=401,
                content={
                    "success": False,
                    "message": "Invalid token payload",
                    "data": {}
                },
            )
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return JSONResponse(
                status_code=401,
                content={
                    "success": False,
                    "message": "User not found",
                    "data": {}
                },
            )

        request.state.user = user
        response = await call_next(request)
        return response
    except JWTError:
        return JSONResponse(
            status_code=401,
            content={
                "success": False,
                "message": "Invalid or expired token",
                "data": {}
            },
        )
    finally:
        db.close()