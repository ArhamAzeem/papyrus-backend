from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.middleware import auth_middleware
from fastapi.openapi.utils import get_openapi
from fastapi.staticfiles import StaticFiles
from app.api.v1.routes import auth_routes
from app.api.v1.routes.admin import auth_routes as admin_auth_routes
from app.api.v1.routes.admin import genre_routes as admin_genre_routes
from app.api.v1.routes.admin import author_routes as admin_author_routes
from app.api.v1.routes.admin import book_routes as admin_book_routes
from app.db.session import engine
from app.db import base
from app.core.admin_middleware import admin_auth_middleware
from app.db.seeders.seed_admin import seed_admin
from sqlalchemy import create_engine, text

base.Base.metadata.create_all(bind=engine)
seed_admin()

app = FastAPI(
    title="Papyrus API",
    description="""
    Papyrus API Documentation

    This API powers the Papyrus Book Store App.
    It includes:
    - User authentication and email verification
    - Password recovery
    - Profile management
    - Secure token-based authentication (JWT)
    - Admin and user role segregation
    """,
    version="1.0.0",
    contact={
        "name": "Papyrus Dev Team",
        "url": "https://github.com/ArhamAzeem/Papyrus",
        "email": "arhamazeem318@gmail.com",
    },
    license_info={
        "name": "MIT License",
    },
)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.middleware("http")(auth_middleware)
app.middleware("http")(admin_auth_middleware)

app.include_router(auth_routes.router, prefix="/api/v1")

app.include_router(admin_auth_routes.router, prefix="/api/v1")
app.include_router(admin_genre_routes.router, prefix="/api/v1")
app.include_router(admin_author_routes.router, prefix="/api/v1")
app.include_router(admin_book_routes.router, prefix="/api/v1")

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Papyrus API",
        version="1.0.0",
        description="Papyrus Book Store API with authentication and admin routes.",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    for path in openapi_schema["paths"].values():
        for method in path.values():
            method["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

@app.get("/")
def read_root():
    with engine.connect() as conn:
        version = conn.execute(text("SELECT VERSION()")).scalar_one()
        return {"message": "Connected to DB", "mysql_version": version}