import os
import sys
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# --- LÓGICA DE PORTABILIDADE PARA O PENDRIVE ---
if getattr(sys, 'frozen', False):
    base_path = os.path.dirname(sys.executable)
else:
    base_path = os.path.dirname(os.path.abspath(__file__))

DB_PATH = os.path.join(base_path, "livro_de_erros.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

# --- BANCO DE DADOS ---
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Incidente(Base):
    __tablename__ = "incidentes"
    id = Column(Integer, primary_key=True)
    codigo = Column(String)
    descricao = Column(Text)  # "O que aconteceu"
    causas = Column(Text)     # "Possíveis Causas"
    solucao = Column(Text)    # "Soluções"
    tags = Column(String)
    data = Column(DateTime, default=datetime.now)

Base.metadata.create_all(bind=engine)

# --- APP ---
app = FastAPI()
templates = Jinja2Templates(directory=os.path.join(base_path, "templates"))

@app.get("/", response_class=HTMLResponse)
async def home(request: Request, busca: str = ""):
    db = SessionLocal()
    query = db.query(Incidente)
    if busca:
        # Pesquisa no código, na descrição ou nas tags
        query = query.filter(
            Incidente.codigo.contains(busca) | 
            Incidente.descricao.contains(busca) | 
            Incidente.tags.contains(busca)
        )
    erros = query.order_by(Incidente.data.desc()).all()
    return templates.TemplateResponse("index.html", {"request": request, "erros": erros})

@app.post("/salvar")
async def salvar(
    codigo: str = Form(...),
    descricao: str = Form(...),
    causas: str = Form(...),
    solucao: str = Form(...),
    #tags: str = Form(...)
):
    db = SessionLocal()
    novo = Incidente(codigo=codigo, descricao=descricao, causas=causas, solucao=solucao) #tags=tags)
    db.add(novo)
    db.commit()
    return RedirectResponse(url="/", status_code=303)