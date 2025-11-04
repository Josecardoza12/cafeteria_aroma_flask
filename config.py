import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")

    uri = os.environ.get("DATABASE_URL")
    if uri and uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql+psycopg2://", 1)

    # Forzar SSL si se usa PostgreSQL (Render exige conexión cifrada)
    if uri and "render.com" in uri:
        if "?sslmode=require" not in uri:
            uri += "?sslmode=require"

    SQLALCHEMY_DATABASE_URI = uri or f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
