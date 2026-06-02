"""
Data Warehouse Models with PostGIS spatial support
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, Float, Integer, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from geoalchemy2.shape import to_shape

from models.base import Base


class Deal(Base):
    """Deal entity for deal-analysis AI"""
    __tablename__ = "deals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    deal_value = Column(Float)
    deal_type = Column(String(50))  # acquisition, merger, joint_venture, etc.
    status = Column(String(50), default="active")  # active, closed, cancelled

    # Spatial data
    location = Column(Geometry(geometry_type="POINT", srid=4326))

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    properties = relationship("Property", back_populates="deal", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_deals_status", "status"),
        Index("idx_deals_location", "location", postgresql_using="gist"),
    )


class Property(Base):
    """Property entity linked to deals"""
    __tablename__ = "properties"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    deal_id = Column(UUID(as_uuid=True), ForeignKey("deals.id", ondelete="CASCADE"), nullable=False)

    address = Column(String(500))
    city = Column(String(100))
    state = Column(String(50))
    country = Column(String(100))
    postal_code = Column(String(20))

    # Spatial boundary
    boundary = Column(Geometry(geometry_type="POLYGON", srid=4326))

    # Property metrics
    area_sqft = Column(Float)
    bedrooms = Column(Integer)
    bathrooms = Column(Float)
    year_built = Column(Integer)
    property_type = Column(String(50))  # residential, commercial, industrial

    # Valuation
    estimated_value = Column(Float)
    price_per_sqft = Column(Float)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("idx_properties_deal_id", "deal_id"),
        Index("idx_properties_boundary", "boundary", postgresql_using="gist"),
        Index("idx_properties_city_state", "city", "state"),
    )


class DealAnalysis(Base):
    """AI analysis results for deals"""
    __tablename__ = "deal_analyses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    deal_id = Column(UUID(as_uuid=True), ForeignKey("deals.id", ondelete="CASCADE"), nullable=False)

    # AI model output
    analysis_type = Column(String(100))  # valuation, risk, market_comparison
    model_version = Column(String(50))

    # Results
    score = Column(Float)  # 0-100 confidence score
    summary = Column(Text)
    details = Column(Text)  # JSON blob with detailed metrics

    # Processing metadata
    processed_at = Column(DateTime, default=datetime.utcnow)
    processing_time_ms = Column(Integer)

    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_analysis_deal_id", "deal_id"),
        Index("idx_analysis_type", "analysis_type"),
    )


class PipelineRun(Base):
    """ETL pipeline execution tracking"""
    __tablename__ = "pipeline_runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pipeline_name = Column(String(100), nullable=False)
    status = Column(String(50), default="running")  # running, success, failed
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    error_message = Column(Text)

    # Metrics
    records_processed = Column(Integer, default=0)
    records_failed = Column(Integer, default=0)

    __table_args__ = (
        Index("idx_pipeline_runs_name", "pipeline_name"),
        Index("idx_pipeline_runs_status", "status"),
    )