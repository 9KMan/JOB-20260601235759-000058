"""
Tests for deal analysis models
"""
import uuid
from datetime import datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Base, Deal, Property, DealAnalysis, PipelineRun


@pytest.fixture
def engine():
    """Create test engine with in-memory SQLite"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def session(engine):
    """Create test session"""
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


class TestDealModel:
    def test_create_deal(self, session):
        """Test deal creation"""
        deal = Deal(
            id=uuid.uuid4(),
            name="Test Deal",
            description="A test deal",
            deal_value=1000000.0,
            deal_type="acquisition",
            status="active",
        )
        session.add(deal)
        session.commit()

        saved = session.query(Deal).filter_by(name="Test Deal").first()
        assert saved is not None
        assert saved.deal_value == 1000000.0
        assert saved.status == "active"

    def test_deal_timestamps(self, session):
        """Test deal has created_at and updated_at"""
        deal = Deal(name="Timestamp Test", status="active")
        session.add(deal)
        session.commit()

        assert deal.created_at is not None
        assert deal.updated_at is not None


class TestPropertyModel:
    def test_create_property_with_deal(self, session):
        """Test property linked to deal"""
        deal = Deal(name="Deal for Property", status="active")
        session.add(deal)
        session.commit()

        prop = Property(
            deal_id=deal.id,
            address="123 Main St",
            city="Boston",
            state="MA",
            country="USA",
            area_sqft=2000.0,
        )
        session.add(prop)
        session.commit()

        saved = session.query(Property).filter_by(city="Boston").first()
        assert saved is not None
        assert saved.deal_id == deal.id


class TestPipelineRunModel:
    def test_create_pipeline_run(self, session):
        """Test pipeline run tracking"""
        run = PipelineRun(
            pipeline_name="test_pipeline",
            status="running",
            records_processed=0,
        )
        session.add(run)
        session.commit()

        assert run.id is not None
        assert run.status == "running"
        assert run.started_at is not None


class TestPipelineResult:
    def test_pipeline_result_dataclass(self):
        """Test PipelineResult can be created"""
        from services.pipelines import PipelineResult

        result = PipelineResult(
            success=True,
            records_processed=100,
            records_failed=5,
            duration_ms=1500,
        )
        assert result.success is True
        assert result.records_processed == 100
        assert result.records_failed == 5
        assert result.duration_ms == 1500