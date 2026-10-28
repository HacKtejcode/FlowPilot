from fastapi.testclient import TestClient

from main import app

client=TestClient(app)

#Basic testing

def test_home_endpoint():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["project"] == "FlowPilot"
    assert response.json()["status"] == "running"


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_readiness_endpoint():
    response = client.get("/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


#test case to creation of deployment

def test_create_deployment():
    response = client.post(
        "/deployments",
        json={
            "service_name": "payment-api",
            "environment": "staging",
            "version": "1.0.0",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["service_name"] == "payment-api"
    assert data["environment"] == "staging"
    assert data["version"] == "1.0.0"
    assert data["status"] == "pending"
    assert "id" in data



#to get list of deployments 

def test_list_deployments():
    create_response = client.post(
        "/deployments",
        json={
            "service_name": "inventory-api",
            "environment": "testing",
            "version": "1.0.0",
        },
    )

    assert create_response.status_code == 201

    response = client.get("/deployments")

    assert response.status_code == 200

    data = response.json()

    assert data["count"] >= 1
    assert any(
        deployment["service_name"] == "inventory-api"
        for deployment in data["deployments"]
    )


#Adding testcases for id

def test_get_deployment_by_id():
    create_response = client.post(
        "/deployments",
        json={
            "service_name": "orders-api",
            "environment": "staging",
            "version": "2.0.0",
        },
    )

    assert create_response.status_code == 201

    created_deployment = create_response.json()
    deployment_id = created_deployment["id"]

    response = client.get(f"/deployments/{deployment_id}")

    assert response.status_code == 200
    assert response.json() == created_deployment


def test_get_nonexistent_deployment():
    response = client.get(
        "/deployments/00000000-0000-0000-0000-000000000000"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Deployment not found"


#adding testcases for status

def test_update_deployment_status():
    create_response = client.post(
        "/deployments",
        json={
            "service_name": "checkout-api",
            "environment": "staging",
            "version": "1.0.0",
        },
    )

    deployment_id = create_response.json()["id"]

    response = client.patch(
        f"/deployments/{deployment_id}/status",
        json={"status": "running"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "running"


def test_update_nonexistent_deployment():
    response = client.patch(
        "/deployments/00000000-0000-0000-0000-000000000000/status",
        json={"status": "running"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Deployment not found"




