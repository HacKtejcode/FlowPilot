
import sqlite3
from pathlib import Path
from typing import Literal
from uuid import uuid4

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field


app = FastAPI(
    title="FlowPilot",
    description="A DevOps learning and deployment management API",
    version="1.0.0",
)

DATABASE_PATH = Path(__file__).resolve().parent / "flowpilot.db"


class DeploymentCreate(BaseModel):
    service_name: str = Field(min_length=2, max_length=100)
    environment: str = Field(min_length=2, max_length=30)
    version: str = Field(min_length=1, max_length=50)


class DeploymentStatusUpdate(BaseModel):
    status: Literal["pending", "running", "successful", "failed"]


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS deployments (
                id TEXT PRIMARY KEY,
                service_name TEXT NOT NULL,
                environment TEXT NOT NULL,
                version TEXT NOT NULL,
                status TEXT NOT NULL
                    CHECK (status IN (
                        'pending', 'running', 'successful', 'failed'
                    ))
            )
            """
        )


def row_to_dict(row):
    return dict(row) if row is not None else None


init_db()


@app.get("/")
def home():
    return {
        "project": "FlowPilot",
        "message": "Welcome to FlowPilot!",
        "status": "running",
        "version": "1.0.0",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/ready")
def readiness_check():
    return {"status": "ready"}


@app.post("/deployments", status_code=status.HTTP_201_CREATED)
def create_deployment(deployment: DeploymentCreate):
    deployment_id = str(uuid4())

    deployment_record = {
        "id": deployment_id,
        "service_name": deployment.service_name,
        "environment": deployment.environment,
        "version": deployment.version,
        "status": "pending",
    }

    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO deployments
                (id, service_name, environment, version, status)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                deployment_record["id"],
                deployment_record["service_name"],
                deployment_record["environment"],
                deployment_record["version"],
                deployment_record["status"],
            ),
        )

    return deployment_record


@app.get("/deployments")
def list_deployments():
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT * FROM deployments ORDER BY rowid DESC"
        ).fetchall()

    records = [row_to_dict(row) for row in rows]

    return {
        "count": len(records),
        "deployments": records,
    }


@app.get("/deployments/{deployment_id}")
def get_deployment(deployment_id: str):
    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM deployments WHERE id = ?",
            (deployment_id,),
        ).fetchone()

    deployment = row_to_dict(row)

    if deployment is None:
        raise HTTPException(
            status_code=404,
            detail="Deployment not found",
        )

    return deployment


@app.patch("/deployments/{deployment_id}/status")
def update_deployment_status(
    deployment_id: str,
    status_update: DeploymentStatusUpdate,
):
    with get_connection() as connection:
        cursor = connection.execute(
            "UPDATE deployments SET status = ? WHERE id = ?",
            (status_update.status, deployment_id),
        )

        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="Deployment not found",
            )

        row = connection.execute(
            "SELECT * FROM deployments WHERE id = ?",
            (deployment_id,),
        ).fetchone()

    return row_to_dict(row)
