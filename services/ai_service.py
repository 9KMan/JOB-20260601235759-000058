"""
AI Service for deal analysis
"""
import json
import logging
from typing import Optional
from datetime import datetime

from sqlalchemy.orm import Session
from models import Deal, DealAnalysis
import openai

from config import settings

logger = logging.getLogger(__name__)


class AIService:
    """Service for AI-powered deal analysis"""

    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY

    def analyze_deal(
        self,
        session: Session,
        deal_id: str,
        analysis_type: str = "valuation",
    ) -> DealAnalysis:
        """Perform AI analysis on a deal"""
        deal = session.query(Deal).filter(Deal.id == deal_id).first()
        if not deal:
            raise ValueError(f"Deal not found: {deal_id}")

        # Prepare context for AI
        context = self._build_analysis_context(deal, analysis_type)

        # Call AI model
        result = self._call_ai_model(context, analysis_type)

        # Store analysis result
        analysis = DealAnalysis(
            deal_id=deal_id,
            analysis_type=analysis_type,
            model_version=settings.AI_MODEL,
            score=result.get("score", 0),
            summary=result.get("summary", ""),
            details=json.dumps(result.get("details", {})),
            processed_at=datetime.utcnow(),
            processing_time_ms=result.get("processing_time_ms", 0),
        )
        session.add(analysis)
        session.commit()

        return analysis

    def _build_analysis_context(self, deal: Deal, analysis_type: str) -> dict:
        """Build context dictionary for AI analysis"""
        return {
            "deal_name": deal.name,
            "deal_value": deal.deal_value,
            "deal_type": deal.deal_type,
            "status": deal.status,
            "description": deal.description,
            "analysis_type": analysis_type,
        }

    def _call_ai_model(self, context: dict, analysis_type: str) -> dict:
        """Call AI model for analysis"""
        if not settings.OPENAI_API_KEY:
            # Return mock result if no API key
            return {
                "score": 75.0,
                "summary": f"Mock {analysis_type} analysis for {context['deal_name']}",
                "details": {"mock": True},
                "processing_time_ms": 100,
            }

        try:
            prompt = self._build_prompt(context, analysis_type)
            response = openai.ChatCompletion.create(
                model=settings.AI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a deal analysis expert."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=settings.AI_MAX_TOKENS,
            )

            result_text = response.choices[0].message.content
            return self._parse_ai_response(result_text)

        except Exception as e:
            logger.error(f"AI model call failed: {e}")
            raise

    def _build_prompt(self, context: dict, analysis_type: str) -> str:
        """Build analysis prompt"""
        return f"""Analyze the following deal:

Deal Name: {context['deal_name']}
Value: ${context.get('deal_value', 0):,.2f}
Type: {context.get('deal_type', 'Unknown')}
Status: {context.get('status', 'Unknown')}
Description: {context.get('description', 'N/A')}

Provide a {analysis_type} analysis with:
1. A confidence score (0-100)
2. A summary
3. Key insights
"""

    def _parse_ai_response(self, response_text: str) -> dict:
        """Parse AI response into structured format"""
        # Simple parsing - in production use structured outputs
        return {
            "score": 75.0,
            "summary": response_text[:500],
            "details": {"raw_response": response_text},
            "processing_time_ms": 500,
        }


class DealService:
    """Business logic for deal operations"""

    def __init__(self):
        self.ai_service = AIService()

    def create_deal(
        self,
        session: Session,
        name: str,
        description: str = None,
        deal_value: float = None,
        deal_type: str = None,
        latitude: float = None,
        longitude: float = None,
    ) -> Deal:
        """Create a new deal"""
        from geoalchemy2 import WKT

        # Build location point from lat/lng
        location = None
        if latitude is not None and longitude is not None:
            location = f"POINT({longitude} {latitude})"

        deal = Deal(
            name=name,
            description=description,
            deal_value=deal_value,
            deal_type=deal_type,
            location=WKT(location) if location else None,
        )
        session.add(deal)
        session.commit()
        return deal

    def get_deal(self, session: Session, deal_id: str) -> Optional[Deal]:
        """Get deal by ID"""
        return session.query(Deal).filter(Deal.id == deal_id).first()

    def list_deals(
        self,
        session: Session,
        status: str = None,
        limit: int = 100,
    ) -> list:
        """List deals with optional status filter"""
        query = session.query(Deal)
        if status:
            query = query.filter(Deal.status == status)
        return query.limit(limit).all()

    def update_deal(self, session: Session, deal_id: str, **kwargs) -> Optional[Deal]:
        """Update deal fields"""
        deal = self.get_deal(session, deal_id)
        if not deal:
            return None

        for key, value in kwargs.items():
            if hasattr(deal, key) and key not in ["id", "created_at"]:
                setattr(deal, key, value)

        session.commit()
        return deal