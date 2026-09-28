from sqlmodel import Session, select, create_engine
from backend.models import SMEAssessment

engine = create_engine("sqlite:///assessment_v2.db")
with Session(engine) as session:
    rows = session.exec(select(SMEAssessment.id).limit(5)).all()
    print("\n".join(rows))
