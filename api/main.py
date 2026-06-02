"""
FastAPI REST API for Deal Analysis
"""
from datetime import datetime, timedelta
from typing import Optional
import uuid

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
import jwt

from config import settings
from models import Base, Deal, Property, DealAnalysis
from services import AIService, DealService
from database import get_db, engine

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Deal Analysis API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# JWT Security
security = HTTPBearer()


def create_token(user_id: str) -> str:
    """Create JWT token"""
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRATION_HOURS),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Verify JWT token"""
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


# Pydantic schemas
class DealCreate(BaseModel):
    name: str
    description: Optional[str] = None
    deal_value: Optional[float] = None
    deal_type: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class DealUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    deal_value: Optional[float] = None
    deal_type: Optional[str] = None
    status: Optional[str] = None


class DealResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    deal_value: Optional[float]
    deal_type: Optional[str]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class AnalysisRequest(BaseModel):
    analysis_type: str = Field(default="valuation")


class AnalysisResponse(BaseModel):
    id: str
    deal_id: str
    analysis_type: str
    score: float
    summary: str
    processed_at: datetime


# Auth endpoints
@app.post("/api/v1/auth/token")
def get_token(user_id: str):
    """Get JWT token (simplified auth for demo)"""
    token = create_token(user_id)
    return {"access_token": token, "token_type": "bearer"}


# Deal endpoints
@app.get("/api/v1/deals", response_model=list[DealResponse])
def list_deals(
    status: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db),
    token: dict = Depends(verify_token),
):
    """List all deals with optional status filter"""
    service = DealService()
    deals = service.list_deals(db, status=status, limit=limit)
    return deals


@app.get("/api/v1/deals/{deal_id}", response_model=DealResponse)
def get_deal(
    deal_id: str,
    db: Session = Depends(get_db),
    token: dict = Depends(verify_token),
):
    """Get a specific deal by ID"""
    service = DealService()
    deal = service.get_deal(db, deal_id)
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    return deal


@app.post("/api/v1/deals", response_model=DealResponse, status_code=status.HTTP_201_CREATED)
def create_deal(
    deal: DealCreate,
    db: Session = Depends(get_db),
    token: dict = Depends(verify_token),
):
    """Create a new deal"""
    service = DealService()
    new_deal = service.create_deal(
        db,
        name=deal.name,
        description=deal.description,
        deal_value=deal.deal_value,
        deal_type=deal.deal_type,
        latitude=deal.latitude,
        longitude=deal.longitude,
    )
    return new_deal


@app.patch("/api/v1/deals/{deal_id}", response_model=DealResponse)
def update_deal(
    deal_id: str,
    deal_update: DealUpdate,
    db: Session = Depends(get_db),
    token: dict = Depends(verify_token),
):
    """Update a deal"""
    service = DealService()
    updated = service.update_deal(db, deal_id, **deal_update.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Deal not found")
    return updated


# Analysis endpoints
@app.post("/api/v1/deals/{deal_id}/analyze", response_model=AnalysisResponse)
def analyze_deal(
    deal_id: str,
    request: AnalysisRequest,
    db: Session = Depends(get_db),
    token: dict = Depends(verify_token),
):
    """Run AI analysis on a deal"""
    ai_service = AIService()
    try:
        analysis = ai_service.analyze_deal(db, deal_id, request.analysis_type)
        return analysis
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/deals/{deal_id}/analyses", response_model=list[AnalysisResponse])
def list_analyses(
    deal_id: str,
    db: Session = Depends(get_db),
    token: dict = Depends(verify_token),
):
    """List all analyses for a deal"""
    analyses = db.query(DealAnalysis).filter(DealAnalysis.deal_id == deal_id).all()
    return analyses


# Health check (no auth required)
@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}