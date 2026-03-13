from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime
from database import Base, engine

class Incidente(Base):
    __tablename__ = "incidentes"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String, index=True)
    descricao = Column(Text)
    causas = Column(Text)
    solucao = Column(Text)
    tags = Column(String)
    data = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)