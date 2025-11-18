from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from fastapi import Form

from app.db.session import SessionLocal
from app.models.company import Company
from app.schemas.company import CompanyCreate, CompanyRead, CompanyLogin

router = APIRouter(prefix="/company", tags=["company"])

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# ------------------------
# REGISTER COMPANY
# ------------------------
@router.post("/register", response_model=CompanyRead)
def register_company(payload: CompanyCreate, db: Session = Depends(get_db)):

    company_by_email = db.query(Company).filter(
        Company.email == payload.email
    ).first()

    if company_by_email:
        raise HTTPException(status_code=400, detail="Company email already registered")

    company_by_name = db.query(Company).filter(
        Company.name == payload.name
    ).first()

    if company_by_name:
        raise HTTPException(status_code=400, detail="Company name already exists")

    hashed_password = pwd_context.hash(payload.password)

    company = Company(
        name=payload.name,
        email=payload.email,
        password_hash=hashed_password,
        description=payload.description
    )

    db.add(company)
    db.commit()
    db.refresh(company)

    return company


# ------------------------
# LOGIN COMPANY
# ------------------------
@router.post("/login", response_model=CompanyRead)
def login_company(payload: CompanyLogin, db: Session = Depends(get_db)):
    print("Login attempt for email:", payload.email)
    # Find company by email
    company = db.query(Company).filter(
        Company.email == payload.email
    ).first()
    print(company)

    if not company:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Verify password
    if not verify_password(payload.password, company.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return company
