import pytest
from fastapi.testclient import TestClient
import os

APIKEY = "test"

os.environ["APIKEY"] = APIKEY
os.environ["DEV"] = "True"
os.environ["NOTIFY_MAIL"] = "False"
os.environ["NOTIFY_DISCORD"] = "False"
os.environ["NOTIFY_SLACK"] = "False"
os.environ["DATABASE_URL"] = "postgresql://root:root@localhost:5432/test_db"
from server.app import app,apiPrefix


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

def test_all_jobs(client):
    response = client.get(apiPrefix + "/jobs")
    assert response.status_code == 200
    assert len(response.json()) == 5
    assert response.json()[0]["id"] == "appwrite"
    assert len(response.json()[0]["runsResults"]) == 10
    assert response.json()[1]["id"] == "mailcow-local"
    assert len(response.json()[1]["runsResults"]) == 2
    assert response.json()[2]["id"] == "mailcow-s3"
    assert len(response.json()[2]["runsResults"]) == 2
    assert response.json()[3]["id"] == "restic"
    assert len(response.json()[3]["runsResults"]) == 3
    assert response.json()[4]["id"] == "should_expire"
    assert len(response.json()[4]["runsResults"]) == 3
    
def test_single_job(client):
    response = client.get(apiPrefix + "/jobs/mailcow-local")
    assert response.status_code == 200
    assert response.json()["job"]["id"] == "mailcow-local"
    assert len(response.json()["job"]["runsResults"]) == 2
    assert response.json()["job"]["runsResults"][0]["output"] == "Neuester Eintrag"
    
def test_single_job_fail_by_id(client):
    response = client.get(apiPrefix + "/jobs/mailcow-local-2")
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid Job ID"
    

    
    
def test_insert_result(client):
    response = client.post(apiPrefix + "/jobs/insert", json={"job_id": "mailcow-local", "is_success": True, "output": "Test Message", "command": "echo 'Hallo Welt'", "started_at": "2021-01-01T00:00:00.000Z", "finished_at": "2021-01-01T00:00:00.000Z", "runtime": 2.0}, headers={"api-key": APIKEY})
    print("Test insert result", response.json())            
    job = response.json()["job"]
    insertedRun = response.json()["insertedRun"]
    responseMessage = response.json()["response"]
    assert response.status_code == 201
    assert job["id"] == "mailcow-local"
    assert job["is_waiting"] == False
    assert job["has_failed"] == False
    assert job["is_running"] == False
    assert insertedRun["job_id"] == "mailcow-local"
    assert insertedRun["is_success"] == True
    assert insertedRun["error"] == ""
    assert insertedRun["output"] == "Test Message"
    assert insertedRun["command"] == "echo 'Hallo Welt'"
    assert insertedRun["started_at"] == "2021-01-01T00:00:00+00:00" # Convert to UTC
    assert insertedRun["finished_at"] == "2021-01-01T00:00:00+00:00" 
    assert insertedRun["id"] != ""
    assert responseMessage == "Job was not waiting -> Notify"
     
def test_job_expire(client):
    response = client.put(apiPrefix + "/jobs/mailcow-local/waiting", headers={"api-key": APIKEY})
    assert response.json()["message"] == "Job waiting state set to: True"
    response = client.post(apiPrefix + "/jobs/mailcow-local/grace_time_expired", headers={"api-key": APIKEY})
    assert response.json()["message"] == "Grace time expired -> Notify"    
    
def test_failed(client):
    # Set waiting
    response = client.put(apiPrefix + "/jobs/mailcow-local/waiting", headers={"api-key": APIKEY})
    assert response.json()["message"] == "Job waiting state set to: True"
    response = client.post(apiPrefix + "/jobs/insert", json={"job_id": "mailcow-local", "is_success": False, "output": "Test Message", "command": "echo 'Hallo Welt'", "started_at": "2021-01-01T00:00:00.000Z", "finished_at": "2021-01-01T00:00:00.000Z", "runtime": 2.0}, headers={"api-key": APIKEY})
    assert response.json()["response"] == "Job failed -> Notify"
    response = client.post(apiPrefix + "/jobs/mailcow-local/grace_time_expired", headers={"api-key": APIKEY})
    assert response.json()["message"] == "Job was not waiting"
    
def test_success(client):
    # Set waiting
    response = client.put(apiPrefix + "/jobs/mailcow-local/waiting", headers={"api-key": APIKEY})
    assert response.json()["message"] == "Job waiting state set to: True"
    # Set job to running
    response = client.post(apiPrefix + "/jobs/start?job_id=mailcow-local", headers={"api-key": APIKEY})
    assert response.json()["message"] == "Job running state set to: True"
    # Check for running
    response = client.get(apiPrefix + "/jobs/mailcow-local")
    assert response.json()["job"]["id"] == "mailcow-local"
    assert response.json()["job"]["is_waiting"] == True
    assert response.json()["job"]["has_failed"] == False
    assert response.json()["job"]["is_running"] == True
    # Insert success
    response = client.post(apiPrefix + "/jobs/insert", json={"job_id": "mailcow-local", "is_success": True, "output": "Test Message", "command": "echo 'Hallo Welt'", "started_at": "2021-01-01T00:00:00.000Z", "finished_at": "2021-01-01T00:00:00.000Z", "runtime": 2.0}, headers={"api-key": APIKEY})
    assert response.json()["response"] == "OK"
    assert response.json()["job"]["id"] == "mailcow-local"
    assert response.json()["job"]["is_waiting"] == False
    assert response.json()["job"]["has_failed"] == False
    assert response.json()["job"]["is_running"] == False
    
def test_success_resolved(client):
    # Set waiting
    response = client.put(apiPrefix + "/jobs/mailcow-local/waiting", headers={"api-key": APIKEY})
    assert response.json()["message"] == "Job waiting state set to: True"
    # Set job to running
    response = client.post(apiPrefix + "/jobs/start?job_id=mailcow-local", headers={"api-key": APIKEY})
    assert response.json()["message"] == "Job running state set to: True"
    # Insert Failed
    response = client.post(apiPrefix + "/jobs/insert", json={"job_id": "mailcow-local", "is_success": False, "output": "Test Message", "command": "echo 'Hallo Welt'", "started_at": "2021-01-01T00:00:00.000Z", "finished_at": "2021-01-01T00:00:00.000Z", "runtime": 2.0}, headers={"api-key": APIKEY})
    assert response.json()["response"] == "Job failed -> Notify"
    assert response.json()["job"]["id"] == "mailcow-local"
    assert response.json()["job"]["is_waiting"] == False
    assert response.json()["job"]["has_failed"] == True
    assert response.json()["job"]["is_running"] == False
    # Insert Success
    response = client.post(apiPrefix + "/jobs/insert", json={"job_id": "mailcow-local", "is_success": True, "output": "Test Message", "command": "echo 'Hallo Welt'", "started_at": "2021-01-01T00:00:00.000Z", "finished_at": "2021-01-01T00:00:00.000Z", "runtime": 2.0}, headers={"api-key": APIKEY})
    assert response.json()["response"] == "Job resolved -> Notify"
    assert response.json()["job"]["id"] == "mailcow-local"
    assert response.json()["job"]["is_waiting"] == False
    assert response.json()["job"]["has_failed"] == False
    assert response.json()["job"]["is_running"] == False

def test_success_not_waiting(client):
    # Set job to running
    response = client.post(apiPrefix + "/jobs/start?job_id=mailcow-local", headers={"api-key": APIKEY})
    assert response.json()["message"] == "Job running state set to: True"
    # Insert Success
    response = client.post(apiPrefix + "/jobs/insert", json={"job_id": "mailcow-local", "is_success": True, "output": "Test Message", "command": "echo 'Hallo Welt'", "started_at": "2021-01-01T00:00:00.000Z", "finished_at": "2021-01-01T00:00:00.000Z", "runtime": 2.0}, headers={"api-key": APIKEY})
    assert response.json()["response"] == "Job was not waiting -> Notify"
    assert response.json()["job"]["id"] == "mailcow-local"
    assert response.json()["job"]["is_waiting"] == False
    assert response.json()["job"]["has_failed"] == False
    assert response.json()["job"]["is_running"] == False
    
    
def insert_fail_by_apikey(client):
    response = client.post(apiPrefix + "/jobs/insert", json={"job_id": "mailcow-local", "is_success": True, "output": "Test Message", "command": "echo 'Hallo Welt'", "started_at": "2021-01-01T00:00:00.000Z", "finished_at": "2021-01-01T00:00:00.000Z", "runtime": 2.0}, headers={"api-key": "wrong"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid API Key"