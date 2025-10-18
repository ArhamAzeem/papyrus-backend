from fastapi_mail import FastMail,MessageSchema,ConnectionConfig
from app.core.config import Setting

conf = ConnectionConfig(
    MAIL_USERNAME=Setting.MAIL_USERNAME,
    MAIL_PASSWORD=Setting.MAIL_PASSWORD,
    MAIL_FROM=Setting.MAIL_FROM,
    MAIL_PORT=Setting.MAIL_PORT,
    MAIL_SERVER=Setting.MAIL_SERVER,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

async def send_verification_email(email:str,token:str):
    verification_url = f"{Setting.APP_URL}/api/v1/auth/verify?token={token}"
    message = MessageSchema(
        subject="Verify your Account",
        recipients=[email],
        body=f"Click the link to verify: {verification_url}",
        subtype="html"
    )
    fm = FastMail(conf)
    await fm.send_message(message)

async def send_reset_email(email:str,token:str):
    verification_url = f"{Setting.APP_URL}/api/v1/auth/reset?token={token}"
    message = MessageSchema(
        subject="Reset your Password",
        recipients=[email],
        body=f"Click the link to reset: {verification_url}",
        subtype="html"
    )
    fm = FastMail(conf)
    await fm.send_message(message)