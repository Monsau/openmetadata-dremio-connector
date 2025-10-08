"""
Unit tests for DremioClient
"""

import pytest
from unittest.mock import Mock, patch
from src.dremio_connector.clients.dremio_client import DremioClient


@pytest.fixture
def dremio_client():
    """Create a DremioClient instance for testing."""
    return DremioClient(
        host='localhost',
        port=9047,
        username='test_user',
        password='test_pass'
    )


def test_client_initialization(dremio_client):
    """Test client initialization."""
    assert dremio_client.host == 'localhost'
    assert dremio_client.port == 9047
    assert dremio_client.username == 'test_user'
    assert dremio_client.base_url == 'http://localhost:9047'


@patch('requests.Session.post')
def test_login_success(mock_post, dremio_client):
    """Test successful login."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'token': 'test_token'}
    mock_post.return_value = mock_response
    
    result = dremio_client._login()
    
    assert result is True
    assert dremio_client.token == 'test_token'
    assert '_dremiotest_token' in dremio_client.session.headers['Authorization']


@patch('requests.Session.post')
def test_login_failure(mock_post, dremio_client):
    """Test failed login."""
    mock_response = Mock()
    mock_response.status_code = 401
    mock_post.return_value = mock_response
    
    result = dremio_client._login()
    
    assert result is False
    assert dremio_client.token is None


@patch('requests.Session.get')
@patch.object(DremioClient, '_login')
def test_get_sources(mock_login, mock_get, dremio_client):
    """Test getting sources."""
    mock_login.return_value = True
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'data': [
            {
                'id': 'source1',
                'containerType': 'SOURCE',
                'path': ['PostgreSQL'],
                'displayName': 'PostgreSQL DB',
                'type': 'POSTGRES'
            }
        ]
    }
    mock_get.return_value = mock_response
    
    sources = dremio_client.get_sources()
    
    assert len(sources) == 1
    assert sources[0]['name'] == 'PostgreSQL'
    assert sources[0]['id'] == 'source1'
