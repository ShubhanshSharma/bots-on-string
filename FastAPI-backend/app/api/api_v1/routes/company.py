# app/api/api_v1/routes/company.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.company import Company
from app.schemas.company import CompanyCreate, CompanyRead

router = APIRouter(prefix="/company", tags=["company"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/create", response_model=CompanyRead)
def create_company(payload: CompanyCreate, db: Session = Depends(get_db)):
    existing = db.query(Company).filter(Company.name == payload.name).first()
    if existing:
        raise HTTPException(400, "Company already exists")
    company = Company(name=payload.name, description=payload.description)
    db.add(company)
    db.commit()
    db.refresh(company)
    return company

@router.get("/{company_id}", response_model=CompanyRead)
def get_company(company_id: int, db: Session = Depends(get_db)):
    company = db.get(Company, company_id)
    if not company:
        raise HTTPException(404, "Not found")
    return company
