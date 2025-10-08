"""
Main CLI entry point for Dremio Connector
"""

import argparse
import sys
from pathlib import Path
from src.dremio_connector.core.dremio_source import DremioSource
from src.dremio_connector.utils.logger import setup_logger
from src.dremio_connector.utils.config import load_config


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Dremio to OpenMetadata Connector',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--config',
        '-c',
        type=str,
        required=True,
        help='Path to configuration file (YAML or JSON)'
    )
    
    parser.add_argument(
        '--log-level',
        '-l',
        type=str,
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='Logging level (default: INFO)'
    )
    
    parser.add_argument(
        '--log-file',
        type=str,
        help='Optional log file path'
    )
    
    parser.add_argument(
        '--test-connection',
        action='store_true',
        help='Test connections only without ingestion'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logger(
        name='dremio_connector',
        level=args.log_level,
        log_file=args.log_file
    )
    
    try:
        # Load configuration
        logger.info(f"Loading configuration from: {args.config}")
        config = load_config(args.config)
        
        # Extract source configuration
        source_config = config.get('source', {}).get('serviceConnection', {}).get('config', {})
        connection_options = source_config.get('connectionOptions', {})
        
        # Merge with workflow config for OpenMetadata
        workflow_config = config.get('workflowConfig', {})
        full_config = {**connection_options, **workflow_config}
        
        # Initialize connector
        logger.info("Initializing Dremio connector...")
        connector = DremioSource(full_config)
        
        # Test connections
        if args.test_connection:
            logger.info("Testing connections...")
            if connector.test_connection():
                logger.info("✅ Connection test successful")
                return 0
            else:
                logger.error("❌ Connection test failed")
                return 1
        
        # Run ingestion
        logger.info("Starting metadata ingestion...")
        results = connector.ingest_metadata()
        
        # Display results
        logger.info("=" * 60)
        logger.info("Ingestion Results:")
        logger.info(f"  Sources ingested: {results['sources']}")
        logger.info(f"  Datasets ingested: {results['datasets']}")
        logger.info(f"  VDS ingested: {results['vds']}")
        
        if results['errors']:
            logger.warning(f"  Errors encountered: {len(results['errors'])}")
            for error in results['errors']:
                logger.warning(f"    - {error}")
        
        logger.info("=" * 60)
        logger.info("✅ Ingestion completed successfully")
        return 0
        
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
