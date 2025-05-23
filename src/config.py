import os
from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv
from pydantic import AnyHttpUrl, PostgresDsn

load_dotenv(os.getenv("ENV_FILE", ".env"))


class Config:
    # Basic project configs
    BASE_DIR = str(Path(os.path.dirname(__file__)).parent)
    PROJECT_NAME: str = "LexiAI Project"
    CONTACT_EMAIL: str = os.environ["CONTACT_EMAIL"]
    PROJECT_DESCRIPTION: str = f"""
        {PROJECT_NAME} API document.
        Contact us at {CONTACT_EMAIL}
    """

    # Server configs
    LOG_LEVEL: str = os.environ["LOG_LEVEL"]
    DEPLOYMENT_ENV: str = os.environ["DEPLOYMENT_ENV"]
    SERVER_PORT: Optional[int] = os.environ["SERVER_PORT"]
    SERVER_HOST: Optional[str or AnyHttpUrl] = os.environ["SERVER_HOST"]

    if DEPLOYMENT_ENV == "DEV":
        BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
            "http://localhost:3000",
            "http://localhost:8080",
            "*",
        ]
    else:
        BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @staticmethod
    def assemble_db_connection():
        return PostgresDsn.build(
            scheme="postgresql",
            username=os.environ["POSTGRES_USER"],
            password=os.environ["POSTGRES_PASSWORD"],
            port=int(os.environ["POSTGRES_PORT"]),
            host=os.environ["POSTGRES_SERVER"],
            path=os.environ["POSTGRES_DB"] or "",
        ).unicode_string()

    ##############################################################################################
    #       ModelBase config is done. if you are adding new domain to this project please make
    # separate config division like made for user below this. if you have different integration
    # please also make sub division.
    ##############################################################################################

    # =============================== User Domain Config =========================================
    JWT_ALGORITHM: str = os.environ["JWT_ALGORITHM"]
    JWT_SECRET_KEY: str = os.environ["JWT_SECRET_KEY"]
    JWT_EXPIRATION_TIME: int = os.environ["JWT_EXPIRATION_TIME"]

    # Google SSO
    GOOGLE_CLIENT_ID: str = os.environ["GOOGLE_CLIENT_ID"]
    GOOGLE_PROJECT_ID: str = os.environ["GOOGLE_PROJECT_ID"]
    GOOGLE_AUTH_URI: str = os.environ["GOOGLE_AUTH_URI"]
    GOOGLE_TOKEN_URI: str = os.environ["GOOGLE_TOKEN_URI"]
    GOOGLE_AUTH_PROVIDER_X509_CERT_URL: str = os.environ[
        "GOOGLE_AUTH_PROVIDER_X509_CERT_URL"
    ]
    GOOGLE_CLIENT_SECRET: str = os.environ["GOOGLE_CLIENT_SECRET"]
    GOOGLE_AUTH_REDIRECT_URI: str = os.environ["GOOGLE_AUTH_REDIRECT_URI"]
    if DEPLOYMENT_ENV == "DEV":
        # to allow http traffic for local development
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    # SMTP Config
    SMTP_SERVER: str = os.environ["SMTP_SERVER"]
    SMTP_PORT: str = os.environ["SMTP_PORT"]
    SMTP_USER: str = os.environ["SMTP_USER"]
    SMTP_PASS: str = os.environ["SMTP_PASS"]
    FROM_MAIL: str = os.environ["FROM_MAIL"]

    # Stripe Config
    STRIPE_API_KEY: str = os.environ["STRIPE_SECRET_KEY"]
    STRIPE_SUCCESS_URL: str = os.environ["STRIPE_SUCCESS_URL"]
    STRIPE_CANCEL_URL: str = os.environ["STRIPE_CANCEL_URL"]
    STRIPE_WEBHOOK_SECRET: str = os.environ["STRIPE_WEBHOOK_SECRET"]

    # Conversation Config
    GROQ_KEY: str = os.environ["GROQ_KEY"]
    TOGETHER_AI_API_KEY: str = os.environ["TOGETHER_AI_API_KEY"]
