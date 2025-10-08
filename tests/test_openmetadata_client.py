"""
Unit tests for OpenMetadataClient
"""

import pytest
from unittest.mock import Mock, patch
from src.dremio_connector.clients.openmetadata_client import OpenMetadataClient


@pytest.fixture
def om_client():
    """Create an OpenMetadataClient instance for testing."""
    return OpenMetadataClient(
        base_url='http://localhost:8585/api',
        jwt_token='test_token'
    )


def test_client_initialization(om_client):
    """Test client initialization."""
    assert om_client.base_url == 'http://localhost:8585/api'
    assert om_client.jwt_token == 'test_token'
    assert 'Authorization' in om_client.session.headers


@patch('requests.Session.get')
def test_health_check_success(mock_get, om_client):
    """Test successful health check."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_get.return_value = mock_response
    
    result = om_client.health_check()
    
    assert result is True


@patch('requests.Session.get')
def test_health_check_failure(mock_get, om_client):
    """Test failed health check."""
    mock_get.side_effect = Exception("Connection error")
    
    result = om_client.health_check()
    
    assert result is False
