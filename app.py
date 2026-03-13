import os
import sys
import uvicorn
import webbrowser
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from database import SessionLocal, db_path
from models import Incidente
from threading import Timer

app = FastAPI()

# Configuração de caminhos para portabilidade (.exe)
base_path = sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
app.mount("/static", StaticFiles(directory=os.path.join(base_path, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(base_path, "templates"))

@app.get("/", response_class=HTMLResponse)
async def home(request: Request, busca: str = "", pagina: int = 1):
    db = SessionLocal()
    query = db.query(Incidente)
    
    # Lógica de Busca
    if busca:
        query = query.filter(Incidente.codigo.contains(busca) | Incidente.descricao.contains(busca))
    
    # Configuração de Paginação (7 itens por página)
    itens_por_pagina = 7
    total = query.count()
    total_paginas = (total + itens_por_pagina - 1) // itens_por_pagina
    if total_paginas == 0: total_paginas = 1
    
    erros = query.order_by(Incidente.data.desc()).offset((pagina-1)*itens_por_pagina).limit(itens_por_pagina).all()
    db.close()
    
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "erros": erros, 
        "busca": busca,
        "pagina": pagina, 
        "total_paginas": total_paginas
    })

@app.post("/salvar")
async def salvar(codigo: str = Form(...), descricao: str = Form(...), causas: str = Form(...), solucao: str = Form(...)):
    db = SessionLocal()
    
    # Proteção de ADS: Verifica se o código já existe para não crashar o banco
    existe = db.query(Incidente).filter(Incidente.codigo == codigo).first()
    if existe:
        db.close()
        # Redireciona com aviso de erro na URL para o Alert do JavaScript
        return RedirectResponse(url="/?erro=duplicado", status_code=303)

    try:
        novo = Incidente(codigo=codigo, descricao=descricao, causas=causas, solucao=solucao, tags="")
        db.add(novo)
        db.commit()
    except Exception as e:
        print(f"Erro ao salvar: {e}")
        db.rollback()
    finally:
        db.close()
        
    return RedirectResponse(url="/?sucesso=true", status_code=303)

@app.post("/atualizar_parcial/{id}")
async def atualizar(id: int, request: Request):
    dados = await request.form()
    db = SessionLocal()
    erro = db.query(Incidente).filter(Incidente.id == id).first()
    if erro:
        for campo, valor in dados.items():
            setattr(erro, campo, valor)
        db.commit()
    db.close()
    return {"status": "ok"}

def open_browser():
    """Abre o navegador automaticamente após 1.5 segundos"""
    webbrowser.open("http://127.0.0.1:8000")

if __name__ == "__main__":
    # Log visual no terminal (Estilo que você finalizou ontem)
    print("-" * 30)
    print("SISTEMA LIVRO DE ERROS ATIVO")
    print(f"Banco de Dados: {db_path}")
    print("Acesse: http://127.0.0.1:8000")
    print("-" * 30)
    
    # Inicia o timer para abrir o navegador
    Timer(1.5, open_browser).start()
    
    # Roda o servidor Uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")