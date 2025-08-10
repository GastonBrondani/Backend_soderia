from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

load_dotenv()  # carga variables de entorno de .env

DATABASE_URL = os.getenv("DATABASE_URL")  # ej: postgresql://admin:fattorbrondani@localhost:5432/soderia

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
