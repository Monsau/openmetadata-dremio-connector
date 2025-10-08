"""
Pytest configuration and fixtures
"""

import pytest
import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


@pytest.fixture
def sample_config():
    """Sample configuration for testing."""
    return {
        'dremioHost': 'localhost',
        'dremioPort': 9047,
        'dremioUsername': 'admin',
        'dremioPassword': 'admin123',
        'openMetadataServerConfig': {
            'hostPort': 'http://localhost:8585/api',
            'securityConfig': {
                'jwtToken': 'test_token'
            }
        },
        'serviceName': 'test-service',
        'include_sources': True,
        'include_vds': True
    }
