package main

import (
	"context"
	"encoding/json"
	"net/http"

	"github.com/gorilla/mux"
	log "github.com/skyface753/cronitor_selfhost/skyLog"
)

func handlerCronResult(w http.ResponseWriter, r *http.Request) {
	var result CronJobResult
	err := json.NewDecoder(r.Body).Decode(&result)
	if err != nil {
		log.Error(err)
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}
	log.Info(result)
	if result.ApiKey != configClient.API_KEY {
		log.Error("Wrong api key")
		http.Error(w, "Wrong api key", http.StatusUnauthorized)
		return
	}
	// Check if all the required fields are set
	if result.JobID == "" {
		log.Error("JobID is empty")
		http.Error(w, "JobID is empty", http.StatusBadRequest)
		return
	}
	// If success is false, error is required
	if !result.Success && result.Error == "" {
		log.Error("Error is empty")
		http.Error(w, "Error is empty", http.StatusBadRequest)
		return
	}
	// Check if the job exists
	if !configClient.JobExists(result.JobID) {
		log.Error("Job does not exist")
		http.Error(w, "Job does not exist", http.StatusBadRequest)
		return
	}
	if !result.Success {
		log.Info("Job failed", result.JobID)
		failedJob(result.JobID, result.Error)
	} else {
		log.Info("Job success", result.JobID)
		successJob(result.JobID)
	}
	// Remove job from waiting
	removeJobFromWaiting(result.JobID)
}

func handlerWaitingJobs(w http.ResponseWriter, r *http.Request) {
	// Dont return null if there are no waiting jobs
	if len(waitingJobs) == 0 {
		json.NewEncoder(w).Encode([]string{})
	} else {
		json.NewEncoder(w).Encode(waitingJobs)
	}
}

func handlerJobStatus(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	jobID := vars["jobID"]
	result, err := influxClient.GetAllForJob(context.Background(), configClient, jobID)
	if err != nil {
		log.Error(err)
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	json.NewEncoder(w).Encode(result)
}

func handlerStatusAllLast(w http.ResponseWriter, r *http.Request) {
	result, err := influxClient.GetAllLastForAllJobs(context.Background(), configClient)
	if err != nil {
		log.Error(err)
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	json.NewEncoder(w).Encode(result)
}

func handlerStatusAllFull(w http.ResponseWriter, r *http.Request) {
	// json.NewEncoder(w).Encode(configClient.JOBS)
	result, err := influxClient.GetAllForAll(context.Background())
	if err != nil {
		log.Error(err)
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	json.NewEncoder(w).Encode(result)
}

func handlerTriggerCheckJob(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	jobID := vars["jobID"]
	// Check if the job exists
	if !configClient.JobExists(jobID) {
		log.Error("Job does not exist")
		http.Error(w, "Job does not exist", http.StatusBadRequest)
		return
	}
	// Check if the job is already waiting
	if checkIsJobWaiting(jobID) {
		log.Error("Job is already waiting")
		http.Error(w, "Job is already waiting", http.StatusBadRequest)
		return
	}
	// Get the job from config
	job := configClient.GetJob(jobID)
	checkService(job)
	json.NewEncoder(w).Encode("OK")
}
