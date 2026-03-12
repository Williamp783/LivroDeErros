import os
import sys
import uvicorn
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# --- CONFIGURAÇÃO DE CAMINHOS (PORTABILIDADE) ---
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
    db_folder = os.path.dirname(sys.executable)
else:
    base_path = os.path.dirname(os.path.abspath(__file__))
    db_folder = base_path

DB_PATH = os.path.join(db_folder, "livro_de_erros.db")
TEMPLATE_PATH = os.path.join(base_path, "templates")
DATABASE_URL = f"sqlite:///{DB_PATH}"

# --- APP FASTAPI (Criado antes das rotas) ---
app = FastAPI()
templates = Jinja2Templates(directory=TEMPLATE_PATH)

# --- ROTA DO FAVICON ---
@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    # Caminho corrigido para buscar na pasta src incluída no .exe
    favicon_path = os.path.join(base_path, "src", "imagemDB.ico")
    return FileResponse(favicon_path)

# --- BANCO DE DADOS ---
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Incidente(Base):
    __tablename__ = "incidentes"
    id = Column(Integer, primary_key=True)
    codigo = Column(String)
    descricao = Column(Text)
    causas = Column(Text)
    solucao = Column(Text)
    tags = Column(String, default="")
    data = Column(DateTime, default=datetime.now)

Base.metadata.create_all(bind=engine)

# --- ROTAS PRINCIPAIS ---
@app.get("/", response_class=HTMLResponse)
async def home(request: Request, busca: str = ""):
    db = SessionLocal()
    query = db.query(Incidente)
    if busca:
        query = query.filter(
            Incidente.codigo.contains(busca) | 
            Incidente.descricao.contains(busca)
        )
    erros = query.order_by(Incidente.data.desc()).all()
    db.close()
    return templates.TemplateResponse("index.html", {"request": request, "erros": erros})

@app.post("/salvar")
async def salvar(
    codigo: str = Form(...),
    descricao: str = Form(...),
    causas: str = Form(...),
    solucao: str = Form(...)
):
    db = SessionLocal()
    novo = Incidente(
        codigo=codigo, 
        descricao=descricao, 
        causas=causas, 
        solucao=solucao, 
        tags=""
    )
    db.add(novo)
    db.commit()
    db.close()
    return RedirectResponse(url="/", status_code=303)

# --- INICIALIZADOR ---
if __name__ == "__main__":
    print("-" * 30)
    print("SISTEMA LIVRO DE ERROS ATIVO")
    print(f"Banco de Dados: {DB_PATH}")
    print("Acesse: http://127.0.0.1:8000")
    print("-" * 30)
    uvicorn.run(app, host="127.0.0.1", port=8000)