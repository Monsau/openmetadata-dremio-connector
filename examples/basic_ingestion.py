"""
Example script showing how to use the Dremio connector programmatically
"""

from src.dremio_connector.core.dremio_source import DremioSource
from src.dremio_connector.utils.logger import setup_logger


def main():
    """Example usage of Dremio connector."""
    
    # Setup logging
    logger = setup_logger(name='example', level='INFO')
    
    # Configuration
    config = {
        # Dremio connection
        'dremioHost': 'localhost',
        'dremioPort': 9047,
        'dremioUsername': 'admin',
        'dremioPassword': 'admin123',
        
        # OpenMetadata connection
        'openMetadataServerConfig': {
            'hostPort': 'http://localhost:8585/api',
            'securityConfig': {
                'jwtToken': 'your-jwt-token-here'
            }
        },
        
        # Service configuration
        'serviceName': 'dremio-example-service',
        
        # Ingestion options
        'include_sources': True,
        'include_vds': True,
        'include_pds': True,
    }
    
    # Initialize connector
    logger.info("Initializing Dremio connector...")
    connector = DremioSource(config)
    
    # Test connections
    logger.info("Testing connections...")
    if not connector.test_connection():
        logger.error("Connection test failed!")
        return
    
    # Run ingestion
    logger.info("Starting metadata ingestion...")
    results = connector.ingest_metadata()
    
    # Display results
    logger.info("=" * 60)
    logger.info("Ingestion Results:")
    logger.info(f"  Sources: {results['sources']}")
    logger.info(f"  Datasets: {results['datasets']}")
    logger.info(f"  VDS: {results['vds']}")
    logger.info("=" * 60)


if __name__ == '__main__':
    main()
