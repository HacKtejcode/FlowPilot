
from uuid import uuid4

from fastapi import FastAPI, status
from pydantic import BaseModel, Field

app = FastAPI(
    title="FlowPilot",
    description="A DevOps learning and deployment management API",
    version="1.0.0",
)


# Request model: defines the data required to create a deployment.
class DeploymentCreate(BaseModel):
    service_name: str = Field(min_length=2, max_length=100)
    environment: str = Field(min_length=2, max_length=30)
    version: str = Field(min_length=1, max_length=50)


# Temporary in-memory storage for deployment records.
deployments = {}


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

    deployments[deployment_id] = deployment_record

    return deployment_record


@app.get("/deployments")
def list_deployments():
    return {
        "count": len(deployments),
        "deployments": list(deployments.values()),
    }


#Retriving a speific deployment

from fastapi import HTTPException
from fastapi import FastAPI,HTTPException,status


@app.get("/deployments/{deployment_id}")
def get_deployment(deployment_id:str):
    deployment=deployments.get(deployment_id)

    
    if deployment is None:
        raise HTTPException(
            status_code=404,
            detail="Deployment not found",
        )

    return deployment

#Adding deployment status as pending

from typing import Literal
from fastapi import FastAPI, HTTPException, status

class DeploymentStatusUpdate(BaseModel):
    status: Literal["pending", "running", "successful", "failed"]



@app.patch("/deployments/{deployment_id}/status")
def update_deployment_status(
    deployment_id: str,
    status_update: DeploymentStatusUpdate,
):
    deployment = deployments.get(deployment_id)

    if deployment is None:
        raise HTTPException(
            status_code=404,
            detail="Deployment not found",
        )

    deployment["status"] = status_update.status

    return deployment
