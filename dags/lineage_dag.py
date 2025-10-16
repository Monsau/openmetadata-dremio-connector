"""
DAG pour l'agent Lineage de Dremio.
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

def lineage_workflow():
    config = {
        "source": {
            "type": "dremio",
            "serviceName": "dremio-lineage",
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
                    "type": "DatabaseLineage",
                    "queryLogDuration": 7,
                    "resultLimit": 1000
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
    f"{uuid.uuid4()}_lineage",
    default_args=default_args,
    description="Extraction du lineage Dremio",
    start_date=datetime.now(),
    schedule_interval="@daily",
    catchup=False
) as dag:
    lineage_task = PythonOperator(
        task_id="lineage_ingestion",
        python_callable=lineage_workflow
    )