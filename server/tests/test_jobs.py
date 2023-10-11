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
    assert len(response.json()) == 3
    assert response.json()[0]["id"] == "should_expired"
    assert len(response.json()[0]["runsResults"]) == 1
    assert response.json()[1]["id"] == "should_fail"
    assert len(response.json()[1]["runsResults"]) == 3
    assert response.json()[2]["id"] == "should_success"
    assert len(response.json()[2]["runsResults"]) == 2
    
def test_single_job(client):
    response = client.get(apiPrefix + "/jobs/should_success")
    assert response.status_code == 200
    assert response.json()["job"]["id"] == "should_success"
    assert len(response.json()["job"]["runsResults"]) == 2
    assert response.json()["job"]["runsResults"][0]["output"] == "Neuester Eintrag"
    
def test_single_job_fail_by_id(client):
    response = client.get(apiPrefix + "/jobs/not_existing")
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid Job ID"
    
def test_list_all_disabled_jobs(client):
    response = client.get(apiPrefix + "/jobs?show_disabled=true")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == "should_be_disabled"
    assert len(response.json()[0]["runsResults"]) == 1

def test_delete_disabled_job(client):
    response = client.delete(apiPrefix + "/jobs/should_be_disabled", headers={"api-key": APIKEY})
    assert response.status_code == 200
    assert response.json()["message"] == "Job deleted"

def test_delete_disabled_job_fail_by_id(client):
    response = client.delete(apiPrefix + "/jobs/not_existing", headers={"api-key": APIKEY})
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid Job ID"

def test_delete_disabled_job_fail_by_apikey(client):
    response = client.delete(apiPrefix + "/jobs/should_be_disabled", headers={"api-key": "wrong"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid API Key"
    
def test_delete_disabled_job_fail_by_enabled(client):
    response = client.delete(apiPrefix + "/jobs/should_success", headers={"api-key": APIKEY})
    assert response.status_code == 400
    assert response.json()["detail"] == "Job is not disabled! Please remove the job from the jobs.json file and restart the server!"
    
def test_insert_result(client):
    response = client.post(apiPrefix + "/jobs/insert", json={"job_id": "should_success", "is_success": True, "output": "Test Message", "command": "echo 'Hallo Welt'", "started_at": "2021-01-01T00:00:00.000Z", "finished_at": "2021-01-01T00:00:00.000Z", "runtime": 2.0}, headers={"api-key": APIKEY})
    job = response.json()["job"]
    insertedRun = response.json()["insertedRun"]
    responseMessage = response.json()["response"]
    assert response.status_code == 201
    assert job["id"] == "should_success"
    assert job["is_waiting"] == False
    assert job["has_failed"] == False
    assert job["is_running"] == False
    assert job["has_expired"] == False
    assert insertedRun["job_id"] == "should_success"
    assert insertedRun["is_success"] == True
    assert insertedRun["error"] == ""
    assert insertedRun["output"] == "Test Message"
    assert insertedRun["command"] == "echo 'Hallo Welt'"
    assert insertedRun["started_at"] == "2021-01-01T00:00:00+00:00" # Convert to UTC
    assert insertedRun["finished_at"] == "2021-01-01T00:00:00+00:00" 
    assert insertedRun["id"] != ""
    assert responseMessage == "Job was not waiting -> Notify"

def test_insert_in_disabled(client):
    response = client.post(apiPrefix + "/jobs/insert", json={"job_id": "should_be_disabled", "is_success": True, "output": "Test Message", "command": "echo 'Hallo Welt'", "started_at": "2021-01-01T00:00:00.000Z", "finished_at": "2021-01-01T00:00:00.000Z", "runtime": 2.0}, headers={"api-key": APIKEY})
    assert response.status_code == 400
    assert response.json()["detail"] == "Job is disabled"
    


def test_job_expire(client):
    response = client.put(apiPrefix + "/jobs/should_expired/waiting", headers={"api-key": APIKEY})
    assert response.json()["message"] == "Job waiting state set to: True"
    response = client.post(apiPrefix + "/jobs/should_expired/grace_time_expired", headers={"api-key": APIKEY})
    assert response.json()["message"] == "Grace time expired -> Notify"    
    response = client.get(apiPrefix + "/jobs/should_expired")
    assert response.json()["job"]["id"] == "should_expired"
    assert response.json()["job"]["is_waiting"] == False
    assert response.json()["job"]["has_failed"] == False
    assert response.json()["job"]["is_running"] == False
    assert response.json()["job"]["has_expired"] == True
    
def test_failed(client):
    # Set waiting
    response = client.put(apiPrefix + "/jobs/should_fail/waiting", headers={"api-key": APIKEY})
    assert response.json()["message"] == "Job waiting state set to: True"
    response = client.post(apiPrefix + "/jobs/insert", json={"job_id": "should_fail", "is_success": False, "output": "Test Message", "command": "echo 'Hallo Welt'", "started_at": "2021-01-01T00:00:00.000Z", "finished_at": "2021-01-01T00:00:00.000Z", "runtime": 2.0}, headers={"api-key": APIKEY})
    assert response.json()["response"] == "Job failed -> Notify"
    response = client.post(apiPrefix + "/jobs/should_fail/grace_time_expired", headers={"api-key": APIKEY})
    assert response.json()["message"] == "Job was not waiting"
    
def test_success(client):
    # Set waiting
    response = client.put(apiPrefix + "/jobs/should_success/waiting", headers={"api-key": APIKEY})
    assert response.json()["message"] == "Job waiting state set to: True"
    # Set job to running
    response = client.post(apiPrefix + "/jobs/start?job_id=should_success", headers={"api-key": APIKEY})
    assert response.json()["message"] == "Job running state set to: True"
    # Check for running
    response = client.get(apiPrefix + "/jobs/should_success")
    assert response.json()["job"]["id"] == "should_success"
    assert response.json()["job"]["is_waiting"] == True
    assert response.json()["job"]["has_failed"] == False
    assert response.json()["job"]["is_running"] == True
    assert response.json()["job"]["has_expired"] == False
    # Insert success
    response = client.post(apiPrefix + "/jobs/insert", json={"job_id": "should_success", "is_success": True, "output": "Test Message", "command": "echo 'Hallo Welt'", "started_at": "2021-01-01T00:00:00.000Z", "finished_at": "2021-01-01T00:00:00.000Z", "runtime": 2.0}, headers={"api-key": APIKEY})
    assert response.json()["response"] == "OK"
    assert response.json()["job"]["id"] == "should_success"
    assert response.json()["job"]["is_waiting"] == False
    assert response.json()["job"]["has_failed"] == False
    assert response.json()["job"]["is_running"] == False
    assert response.json()["job"]["has_expired"] == False
    
def test_success_resolved(client):
    # PREPARE TEST
    # Set waiting
    response = client.put(apiPrefix + "/jobs/should_success/waiting", headers={"api-key": APIKEY})
    assert response.json()["message"] == "Job waiting state set to: True"
    # Set job to running
    response = client.post(apiPrefix + "/jobs/start?job_id=should_success", headers={"api-key": APIKEY})
    assert response.json()["message"] == "Job running state set to: True"
    # Insert Failed
    response = client.post(apiPrefix + "/jobs/insert", json={"job_id": "should_success", "is_success": False, "output": "Test Message", "command": "echo 'Hallo Welt'", "started_at": "2021-01-01T00:00:00.000Z", "finished_at": "2021-01-01T00:00:00.000Z", "runtime": 2.0}, headers={"api-key": APIKEY})
    assert response.json()["response"] == "Job failed -> Notify"
    assert response.json()["job"]["id"] == "should_success"
    assert response.json()["job"]["is_waiting"] == False
    assert response.json()["job"]["has_failed"] == True
    assert response.json()["job"]["is_running"] == False
    assert response.json()["job"]["has_expired"] == False
    # ACTUAL TEST
    # Insert Success
    response = client.post(apiPrefix + "/jobs/insert", json={"job_id": "should_success", "is_success": True, "output": "Test Message", "command": "echo 'Hallo Welt'", "started_at": "2021-01-01T00:00:00.000Z", "finished_at": "2021-01-01T00:00:00.000Z", "runtime": 2.0}, headers={"api-key": APIKEY})
    assert response.json()["response"] == "Job resolved -> Notify"
    assert response.json()["job"]["id"] == "should_success"
    assert response.json()["job"]["is_waiting"] == False
    assert response.json()["job"]["has_failed"] == False
    assert response.json()["job"]["is_running"] == False
    assert response.json()["job"]["has_expired"] == False

def test_success_not_waiting(client):
    # Set job to running
    response = client.post(apiPrefix + "/jobs/start?job_id=should_success", headers={"api-key": APIKEY})
    assert response.json()["message"] == "Job running state set to: True"
    # Insert Success
    response = client.post(apiPrefix + "/jobs/insert", json={"job_id": "should_success", "is_success": True, "output": "Test Message", "command": "echo 'Hallo Welt'", "started_at": "2021-01-01T00:00:00.000Z", "finished_at": "2021-01-01T00:00:00.000Z", "runtime": 2.0}, headers={"api-key": APIKEY})
    assert response.json()["response"] == "Job was not waiting -> Notify"
    assert response.json()["job"]["id"] == "should_success"
    assert response.json()["job"]["is_waiting"] == False
    assert response.json()["job"]["has_failed"] == False
    assert response.json()["job"]["is_running"] == False
    assert response.json()["job"]["has_expired"] == False
    
    
def test_insert_fail_by_apikey(client):
    response = client.post(apiPrefix + "/jobs/insert", json={"job_id": "should_fail", "is_success": True, "output": "Test Message", "command": "echo 'Hallo Welt'", "started_at": "2021-01-01T00:00:00.000Z", "finished_at": "2021-01-01T00:00:00.000Z", "runtime": 2.0}, headers={"api-key": "wrong"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid API Key"