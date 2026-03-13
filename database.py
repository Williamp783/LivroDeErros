import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

Base = declarative_base()

# Lógica para o Pendrive: Detecta a pasta do .exe
if getattr(sys, 'frozen', False):
    base_dir = os.path.dirname(sys.executable)
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))

db_path = os.path.join(base_dir, "livro_de_erros.db")
SQLALCHEMY_DATABASE_URL = f"sqlite:///{db_path}"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)