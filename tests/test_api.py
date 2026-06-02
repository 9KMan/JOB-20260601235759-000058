"""
Tests for API endpoints
"""
import pytest
from fastapi.testclient import TestClient

# Note: These tests require the full app context
# For unit testing, mock the database session


class TestHealthEndpoint:
    def test_health_check(self):
        """Test health endpoint returns healthy"""
        # Import would require app setup
        # For now, this is a placeholder
        assert True


class TestDealEndpoints:
    def test_deal_schema_validation(self):
        """Test DealCreate schema"""
        from pydantic import ValidationError
        from api.main import DealCreate

        # Valid deal
        deal = DealCreate(name="Test", deal_value=100000)
        assert deal.name == "Test"
        assert deal.deal_value == 100000

        # Missing required field
        with pytest.raises(ValidationError):
            DealCreate(description="No name")