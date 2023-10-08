import pytest
from fastapi.testclient import TestClient
import os
# from server.models.jobs_results import JobResultList
from typing import List


os.environ["APIKEY"] = "test"
os.environ["DEV"] = "True"

from server.app import app,apiPrefix

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

def test_read_main(client):
    response = client.get(apiPrefix + "/jobs")
    assert response.status_code == 200
    assert len(response.json()) == 5
    assert response.json()[0]["id"] == "mailcow-local"
    assert len(response.json()[0]["runsResults"]) == 2
    assert response.json()[1]["id"] == "mailcow-s3"
    assert len(response.json()[1]["runsResults"]) == 2
    assert response.json()[2]["id"] == "appwrite"
    assert len(response.json()[2]["runsResults"]) == 10
    assert response.json()[3]["id"] == "restic"
    assert len(response.json()[3]["runsResults"]) == 3
    assert response.json()[4]["id"] == "should_expire"
    assert len(response.json()[4]["runsResults"]) == 3
    
def test_insert_result(client):
    response = client.post(apiPrefix + "/jobs/insert", json={"job_id": "mailcow-local", "is_success": True, "output": "Test Message", "command": "echo 'Hallo Welt'", "started_at": "2021-01-01T00:00:00.000Z", "finished_at": "2021-01-01T00:00:00.000Z", "runtime": 2.0}, headers={"api-key": "test"})
                                                            
    print("Test insert result", response.json())
    job = response.json()["job"]
    createdJobResult = job["runsResults"][0]
    assert response.status_code == 201
    assert job["id"] == "mailcow-local"
    assert job["is_waiting"] == False
    assert job["has_failed"] == False
    assert createdJobResult["job_id"] == "mailcow-local"
    assert createdJobResult["is_success"] == True
    assert createdJobResult["expired"] == False
    assert createdJobResult["output"] == "Test Message"
    assert createdJobResult["command"] == "echo 'Hallo Welt'"
    assert createdJobResult["started_at"] == "2021-01-01T00:00:00.000Z"
    assert createdJobResult["finished_at"] == "2021-01-01T00:00:00.000Z"
    assert createdJobResult["_id"] != ""
    assert response.json()["response"] == "Job was not waiting -> Notify"
    
def test_expire(client):
    # Set waiting
    response = client.put(apiPrefix + "/jobs/mailcow-local/waiting", headers={"api-key": "test"})
    assert response.json()["message"] == "Job waiting state set to true"
    response = client.post(apiPrefix + "/jobs/mailcow-local/grace_time_expired", headers={"api-key": "test"})
    assert response.json()["message"] == "Job was waiting and did not execute in time!"
    
def test_failed(client):
    # Set waiting
    response = client.put(apiPrefix + "/jobs/mailcow-local/waiting", headers={"api-key": "test"})
    assert response.json()["message"] == "Job waiting state set to true"
    response = client.post(apiPrefix + "/jobs/insert", json={"job_id": "mailcow-local", "is_success": False, "output": "Test Message", "command": "echo 'Hallo Welt'", "started_at": "2021-01-01T00:00:00.000Z", "finished_at": "2021-01-01T00:00:00.000Z"}, headers={"api-key": "test"})
    assert response.json()["response"] == "Job failed -> Notify"
    response = client.post(apiPrefix + "/jobs/mailcow-local/grace_time_expired", headers={"api-key": "test"})
    assert response.json()["message"] == "Job was not waiting"
    
def test_success(client):
    # Set waiting
    response = client.put(apiPrefix + "/jobs/mailcow-local/waiting", headers={"api-key": "test"})
    assert response.json()["message"] == "Job waiting state set to true"
    response = client.post(apiPrefix + "/jobs/insert", json={"job_id": "mailcow-local", "is_success": True, "expired": False, "message": "Test Message", "command": "echo 'Hallo Welt'", "started_at": "2021-01-01T00:00:00.000Z", "finished_at": "2021-01-01T00:00:00.000Z"}, headers={"api-key": "test"})
    assert response.json()["response"] == "Job resolved -> Notify"
    response = client.post(apiPrefix + "/jobs/mailcow-local/grace_time_expired", headers={"api-key": "test"})
    assert response.json()["message"] == "Job was not waiting"
    # AGAIN (should not send resolved mail again)
    response = client.post(apiPrefix + "/jobs/insert", json={"job_id": "mailcow-local", "is_success": True,  "message": "Test Message", "command": "echo 'Hallo Welt'", "started_at": "2021-01-01T00:00:00.000Z", "finished_at": "2021-01-01T00:00:00.000Z"}, headers={"api-key": "test"})
    assert response.json()["response"] == "Job was not waiting -> Notify"
    response = client.post(apiPrefix + "/jobs/mailcow-local/grace_time_expired", headers={"api-key": "test"})
    assert response.json()["message"] == "Job was not waiting"
    # AGAIN (Set waiting -> success -> grace_time_expired)
    response = client.put(apiPrefix + "/jobs/mailcow-local/waiting", headers={"api-key": "test"})
    assert response.json()["message"] == "Job waiting state set to true"
    response = client.post(apiPrefix + "/jobs/insert", json={"job_id": "mailcow-local", "is_success": True, "message": "Test Message", "command": "echo 'Hallo Welt'", "started_at": "2021-01-01T00:00:00.000Z", "finished_at": "2021-01-01T00:00:00.000Z"}, headers={"api-key": "test"})
    assert response.json()["response"] == "OK"
    response = client.post(apiPrefix + "/jobs/mailcow-local/grace_time_expired", headers={"api-key": "test"})
    assert response.json()["message"] == "Job was not waiting"