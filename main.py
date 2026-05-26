from fastapi import FastAPI
from pydantic import BaseModel
import requests
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

load_dotenv()

app = FastAPI()

LANGFLOW_URL = os.getenv("LANGFLOW_URL")
LANGFLOW_API_KEY = os.getenv("LANGFLOW_API_KEY")

DATABASE_URL = "sqlite:///./project_tracker.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class ReportDB(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    team_id = Column(String, index=True)
    session_id = Column(String, index=True)
    report_text = Column(Text)
    agent_response = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


Base.metadata.create_all(bind=engine)


class Report(BaseModel):
    user_id: str
    team_id: str
    text: str


@app.get("/")
def root():
    return {"message": "API работает"}


@app.post("/report")
def send_report(report: Report):
    session_id = f"{report.team_id}_{report.user_id}"
    context_id = report.team_id

    payload = {
        "input_value": report.text,
        "input_type": "chat",
        "output_type": "chat",
        "session_id": session_id,
        "tweaks": {
            "Message History": {
                "session_id": session_id,
                "context_id": context_id
            }
        }
    }

    headers = {
        "Content-Type": "application/json",
        "X-API-Key": LANGFLOW_API_KEY
    }

    response = requests.post(
        LANGFLOW_URL,
        json=payload,
        headers=headers,
        timeout=120
    )

    try:
        data = response.json()
    except Exception:
        return {
            "error": "Langflow вернул не JSON",
            "status_code": response.status_code,
            "raw_response": response.text,
            "sent_to_langflow": payload
        }

    try:
        result_text = data["outputs"][0]["outputs"][0]["results"]["message"]["text"]
    except Exception as e:
        return {
            "error": "Не удалось достать ответ агента",
            "details": str(e),
            "sent_to_langflow": payload,
            "raw_langflow_response": data
        }

    db = SessionLocal()

    db_report = ReportDB(
        user_id=report.user_id,
        team_id=report.team_id,
        session_id=session_id,
        report_text=report.text,
        agent_response=result_text
    )

    db.add(db_report)
    db.commit()
    db.refresh(db_report)

    saved_report_id = db_report.id
    db.close()

    return {
        "id": saved_report_id,
        "user_id": report.user_id,
        "team_id": report.team_id,
        "session_id": session_id,
        "context_id": context_id,
        "sent_text": report.text,
        "agent_response": result_text,
        "saved_to_db": True
    }


@app.get("/reports")
def get_reports():
    db = SessionLocal()
    reports = db.query(ReportDB).order_by(ReportDB.id.desc()).all()
    db.close()

    return [
        {
            "id": r.id,
            "user_id": r.user_id,
            "team_id": r.team_id,
            "session_id": r.session_id,
            "report_text": r.report_text,
            "agent_response": r.agent_response,
            "created_at": r.created_at
        }
        for r in reports
    ]