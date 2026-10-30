"""Airflow DAG: load -> validate -> dbt build -> train.

Each task is a shell command, so the same steps can be run by hand from a terminal.
If a task exits non-zero (a failed validation check or a failed dbt test), Airflow
retries it; if it still fails, every downstream task is skipped, so bad data never
reaches the model.

Set NBI_PROJECT_DIR to the repo path (and NBI_RAW_DIR to the folder with the raw
FHWA .txt files) in the environment that runs Airflow.
"""
from __future__ import annotations

import os
from datetime import datetime, timedelta

try:  # Airflow 3
    from airflow.providers.standard.operators.bash import BashOperator
    from airflow.sdk import DAG
except ImportError:  # Airflow 2
    from airflow import DAG
    from airflow.operators.bash import BashOperator

PROJECT_DIR = os.getenv(
    "NBI_PROJECT_DIR", os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

default_args = {
    "owner": "data-eng",
    "retries": 2,                         # transient failures get two more tries
    "retry_delay": timedelta(minutes=1),
}

with DAG(
    dag_id="nbi_bridge_pipeline",
    description="NBI bridges: raw load, quality gate, dbt star schema, posting model",
    default_args=default_args,
    start_date=datetime(2026, 10, 1),
    schedule=None,                        # run on demand
    catchup=False,
    tags=["nbi", "dbt", "duckdb"],
) as dag:
    load_raw = BashOperator(
        task_id="load_raw",
        bash_command=f"cd '{PROJECT_DIR}' && python pipeline/load_raw.py",
    )
    validate_raw = BashOperator(
        task_id="validate_raw",
        bash_command=f"cd '{PROJECT_DIR}' && python pipeline/validate_raw.py",
        retries=0,                        # bad data won't fix itself: fail fast
    )
    dbt_build = BashOperator(
        task_id="dbt_build",
        # `dbt build` runs seeds, models and tests in dependency order and exits
        # non-zero if any test fails: the second quality gate.
        bash_command=f"cd '{PROJECT_DIR}/nbi_dbt' && dbt build --profiles-dir .",
    )
    train_model = BashOperator(
        task_id="train_model",
        bash_command=f"cd '{PROJECT_DIR}' && python pipeline/train_model.py",
    )

    load_raw >> validate_raw >> dbt_build >> train_model
