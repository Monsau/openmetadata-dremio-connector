"""
DAG pour l'agent DBT de Dremio.
"""
from datetime import datetime, timedelta
import uuid

from airflow import DAG
from airflow.operators.python import PythonOperator

from metadata.workflow.metadata import MetadataWorkflow
from metadata.ingestion.api.workflow import Workflow

default_args = {
    "owner": "dremio",
    "email": [],
    "email_on_failure": False,
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
    "execution_timeout": timedelta(minutes=60)
}

def dbt_workflow():
    config = {
        "source": {
            "type": "dremio",
            "serviceName": "dremio-dbt",
            "serviceConnection": {
                "config": {
                    "type": "Dremio",
                    "hostPort": "host.docker.internal:9047",
                    "username": "admin",
                    "password": "${DREMIO_PASSWORD}",
                    "connectionOptions": {},
                    "connectionArguments": {}
                }
            },
            "sourceConfig": {
                "config": {
                    "type": "Dbt",
                    "dbtConfigSource": {
                        "type": "local",
                        "dbtProjectPath": "/path/to/dbt",
                        "dbtCatalogPath": "target/catalog.json",
                        "dbtManifestPath": "target/manifest.json"
                    }
                }
            }
        },
        "sink": {
            "type": "metadata-rest",
            "config": {}
        },
        "workflowConfig": {
            "loggerLevel": "INFO",
            "openMetadataServerConfig": {
                "hostPort": "http://openmetadata-server:8585/api",
                "authProvider": "openmetadata",
                "securityConfig": {
                    "jwtToken": "${JWT_TOKEN}"
                }
            }
        }
    }
    workflow = MetadataWorkflow.create(config)
    workflow.execute()
    workflow.raise_from_status()
    workflow.print_status()
    workflow.stop()

with DAG(
    f"{uuid.uuid4()}_dbt",
    default_args=default_args,
    description="Intégration DBT avec Dremio",
    start_date=datetime.now(),
    schedule_interval="@daily",
    catchup=False
) as dag:
    dbt_task = PythonOperator(
        task_id="dbt_ingestion",
        python_callable=dbt_workflow
    )