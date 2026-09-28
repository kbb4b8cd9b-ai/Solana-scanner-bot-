import json
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import declarative_base, sessionmaker
from app.settings import settings

engine = create_engine(settings.database_url, connect_args={"check_same_thread":False} if settings.database_url.startswith("sqlite") else {})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Scan(Base):
    __tablename__ = "scans"
    id = Column(Integer, primary_key=True)
    mint = Column(String(64), index=True)
    risk_score = Column(Integer)
    risk_level = Column(String(20))
    payload = Column(Text)
    created_at = Column(String(40), default=lambda: datetime.utcnow().isoformat())

def init_db():
    Base.metadata.create_all(engine)

def save_scan(result):
    db = SessionLocal()
    db.add(Scan(mint=result["mint"], risk_score=result["risk_score"],
                risk_level=result["risk_level"], payload=json.dumps(result)))
    db.commit()
    db.close()

def list_scans(mint=None, limit=50):
    db=SessionLocal()
    q=db.query(Scan).order_by(Scan.id.desc())
    if mint: q=q.filter(Scan.mint==mint)
    rows=q.limit(limit).all()
    out=[json.loads(x.payload) for x in rows]
    db.close()
    return out
