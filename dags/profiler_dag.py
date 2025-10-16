"""
DAG pour l'agent Profiler de Dremio.
"""
from datetime import datetime, timedelta
import uuid

from airflow import DAG
from airflow.operators.python import PythonOperator

from metadata.workflow.profiler import ProfilerWorkflow
from metadata.ingestion.api.workflow import Workflow

default_args = {
    "owner": "dremio",
    "email": [],
    "email_on_failure": False,
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
    "execution_timeout": timedelta(minutes=60)
}

def profiler_workflow():
    config = {
        "source": {
            "type": "dremio",
            "serviceName": "dremio-profiler",
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
                    "type": "Profiler",
                    "generateSampleData": True,
                    "profileSample": 100,
                    "threadCount": 5,
                    "timeoutSeconds": 3600
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
    workflow = ProfilerWorkflow.create(config)
    workflow.execute()
    workflow.raise_from_status()
    workflow.print_status()
    workflow.stop()

with DAG(
    f"{uuid.uuid4()}_profiler",
    default_args=default_args,
    description="Profilage des données Dremio",
    start_date=datetime.now(),
    schedule_interval="@weekly",
    catchup=False
) as dag:
    profiler_task = PythonOperator(
        task_id="profiler_ingestion",
        python_callable=profiler_workflow
    )