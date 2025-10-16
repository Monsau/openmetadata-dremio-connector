"""
Configure tous les agents d'ingestion (Metadata, Profiler, Lineage, DBT) dans Airflow.
"""

import yaml
import uuid
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
from metadata.workflow.metadata import MetadataWorkflow
from metadata.workflow.profiler import ProfilerWorkflow
from metadata.workflow.lineage import LineageWorkflow

# Configuration de base pour OpenMetadata
def get_openmetadata_config():
    return {
        "hostPort": "http://openmetadata-server:8585/api",
        "authProvider": "openmetadata",
        "securityConfig": {
            "jwtToken": "${JWT_TOKEN}"  # À remplacer par le vrai token
        }
    }

# Configuration commune pour tous les agents
def get_base_config(workflow_type, source_type="dremio"):
    return {
        "source": {
            "type": source_type,
            "serviceName": f"dremio-{workflow_type}",
            "serviceConnection": {
                "config": {
                    "type": "Dremio",
                    "hostPort": "host.docker.internal:9047",
                    "username": "admin",
                    "password": "${DREMIO_PASSWORD}",  # À remplacer
                    "connectionOptions": {},
                    "connectionArguments": {}
                }
            }
        },
        "sink": {
            "type": "metadata-rest",
            "config": {}
        },
        "workflowConfig": {
            "loggerLevel": "INFO",
            "openMetadataServerConfig": get_openmetadata_config()
        }
    }

# Configuration spécifique pour chaque type d'agent
def get_metadata_config():
    config = get_base_config("metadata")
    config["source"]["sourceConfig"] = {
        "config": {
            "type": "DatabaseMetadata",
            "databaseFilterPattern": {
                "includes": [".*"],
                "excludes": ["sys", "INFORMATION_SCHEMA"]
            }
        }
    }
    return config

def get_profiler_config():
    config = get_base_config("profiler")
    config["source"]["sourceConfig"] = {
        "config": {
            "type": "Profiler",
            "generateSampleData": True,
            "profileSample": 100,
            "threadCount": 5,
            "timeoutSeconds": 3600
        }
    }
    return config

def get_lineage_config():
    config = get_base_config("lineage")
    config["source"]["sourceConfig"] = {
        "config": {
            "type": "DatabaseLineage",
            "queryLogDuration": 7,
            "resultLimit": 1000
        }
    }
    return config

def get_dbt_config():
    config = get_base_config("dbt")
    config["source"]["sourceConfig"] = {
        "config": {
            "type": "Dbt",
            "dbtConfigSource": {
                "type": "local",
                "dbtProjectPath": "/path/to/dbt",  # À configurer
                "dbtCatalogPath": "target/catalog.json",
                "dbtManifestPath": "target/manifest.json"
            }
        }
    }
    return config

# Fonctions de workflow pour chaque agent
def metadata_ingestion_workflow():
    workflow_config = get_metadata_config()
    workflow = MetadataWorkflow.create(workflow_config)
    workflow.execute()
    workflow.raise_from_status()
    workflow.print_status()
    workflow.stop()

def profiler_workflow():
    workflow_config = get_profiler_config()
    workflow = ProfilerWorkflow.create(workflow_config)
    workflow.execute()
    workflow.raise_from_status()
    workflow.print_status()
    workflow.stop()

def lineage_workflow():
    workflow_config = get_lineage_config()
    workflow = LineageWorkflow.create(workflow_config)
    workflow.execute()
    workflow.raise_from_status()
    workflow.print_status()
    workflow.stop()

def dbt_workflow():
    workflow_config = get_dbt_config()
    workflow = MetadataWorkflow.create(workflow_config)
    workflow.execute()
    workflow.raise_from_status()
    workflow.print_status()
    workflow.stop()

# Configuration commune des DAGs
default_args = {
    "owner": "dremio",
    "email": [],
    "email_on_failure": False,
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
    "execution_timeout": timedelta(minutes=60)
}

# Créer les DAGs pour chaque agent
def create_agent_dags():
    dag_id = str(uuid.uuid4())
    
    # DAG Metadata (exécution quotidienne)
    with DAG(
        f"{dag_id}_metadata",
        default_args=default_args,
        description="Extraction des métadonnées Dremio",
        start_date=datetime.now(),
        schedule_interval="@daily",
        catchup=False
    ) as metadata_dag:
        PythonOperator(
            task_id="metadata_ingestion",
            python_callable=metadata_ingestion_workflow
        )

    # DAG Profiler (exécution hebdomadaire)
    with DAG(
        f"{dag_id}_profiler",
        default_args=default_args,
        description="Profilage des données Dremio",
        start_date=datetime.now(),
        schedule_interval="@weekly",
        catchup=False
    ) as profiler_dag:
        PythonOperator(
            task_id="profiler_ingestion",
            python_callable=profiler_workflow
        )

    # DAG Lineage (exécution quotidienne)
    with DAG(
        f"{dag_id}_lineage",
        default_args=default_args,
        description="Extraction du lineage Dremio",
        start_date=datetime.now(),
        schedule_interval="@daily",
        catchup=False
    ) as lineage_dag:
        PythonOperator(
            task_id="lineage_ingestion",
            python_callable=lineage_workflow
        )

    # DAG DBT (exécution quotidienne)
    with DAG(
        f"{dag_id}_dbt",
        default_args=default_args,
        description="Intégration DBT avec Dremio",
        start_date=datetime.now(),
        schedule_interval="@daily",
        catchup=False
    ) as dbt_dag:
        PythonOperator(
            task_id="dbt_ingestion",
            python_callable=dbt_workflow
        )

    return {
        "metadata": metadata_dag,
        "profiler": profiler_dag,
        "lineage": lineage_dag,
        "dbt": dbt_dag
    }

if __name__ == "__main__":
    dags = create_agent_dags()
    print("✅ DAGs créés avec succès :")