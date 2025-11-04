# config.py
import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")

    # Lee DATABASE_URL del entorno (Render). Si no existe, usa SQLite local.
    uri = os.environ.get("DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

    # Render a veces entrega "postgres://..." -> SQLAlchemy requiere "postgresql+psycopg2://..."
    if uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql+psycopg2://", 1)

    # Forzar SSL en producción si es Postgres y no viene seteado
    if uri.startswith("postgresql") and "sslmode=" not in uri:
        uri += ("&sslmode=require" if "?" in uri else "?sslmode=require")

    SQLALCHEMY_DATABASE_URI = uri
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Evita cortes de conexión (“SSL SYSCALL EOF detected”)
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
