package main

import (
	"context"
	"encoding/json"
	"net/http"

	"github.com/gorilla/mux"
	"github.com/skyface753/cronitor_selfhost/influx"
	log "github.com/skyface753/cronitor_selfhost/skyLog"
)

// CronJobResult ... Result from the runner.sh script
// @Summary CronJobResult
// @Description Result from the runner script
// @Tags Jobs
// @Accept json
// @Produce json
// @Param CronJobResult body CronJobResult true "CronJobResult"
// @Success 200 {object} string "OK"
// @Failure 400 {object} string "Bad Request"
// @Failure 500 {object} string "Internal Server Error"
// @Router /cron/result [post]
func handlerCronResult(w http.ResponseWriter, r *http.Request) {
	enableCors(&w)
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
	w.WriteHeader(http.StatusOK)

}

// WaitingJobs ... Get all waiting jobs
// @Summary Get all waiting jobs
// @Description Get all waiting jobs
// @Tags Jobs
// @Accept json
// @Success 200 {object} []config.Job
// @Failure 400,500 {object} object
// @Router /cron/status/waiting [get]
func handlerWaitingJobs(w http.ResponseWriter, r *http.Request) {
	enableCors(&w)

	// Dont return null if there are no waiting jobs
	if len(waitingJobs) == 0 {
		json.NewEncoder(w).Encode([]string{})
	} else {
		json.NewEncoder(w).Encode(waitingJobs)
	}
}

// JobStatus ... Get all data for a job
// @Summary Get all data for a job
// @Description Get all data for a job
// @Tags Jobs
// @Accept json
// @Param jobID path string true "Job ID"
// @Success 200 {object} influx.UptimeDataMap
// @Failure 400,500 {object} object
// @Router /cron/status/job/{jobID} [get]
func handlerJobStatus(w http.ResponseWriter, r *http.Request) {
	enableCors(&w)

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

// StatusAllLast ... Get last data for all jobs
// @Summary Get last data for all jobs
// @Description Get last data for all jobs
// @Tags Jobs
// @Accept json
// @Success 200 {object} object
// @Failure 400,500 {object} object
// @Router /cron/status/last [get]
func handlerStatusAllLast(w http.ResponseWriter, r *http.Request) {
	enableCors(&w)
	result, err := influxClient.GetAllLastForAllJobs(context.Background(), configClient)
	if err != nil {
		log.Error(err)
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	json.NewEncoder(w).Encode(result)
}

// StatusAllFull ... Get all the data for all jobs
// @Summary Get all the data for all jobs
// @Description Get all the data for all jobs
// @Tags Jobs
// @Accept json
// @Success 200 {object} influx.UptimeDataForAllJobsMap
// @Failure 400,500 {object} object
// @Router /cron/status [get]
func handlerStatusAllFull(w http.ResponseWriter, r *http.Request) { // Result is influx.UptimeDataForAllJobsMap
	enableCors(&w)

	result, err := influxClient.GetAllForAll(context.Background())
	if err != nil {
		log.Error(err)
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	// Add all the jobs that are not in the database
	for _, job := range configClient.JOBS {
		if _, ok := result[job.JobID]; !ok {
			result[job.JobID] = influx.UptimeDataMap{}
		}
	}

	json.NewEncoder(w).Encode(result)
}

// TriggerCheckJob ... Trigger a check for a job
// @Summary Trigger a check for a job
// @Description Trigger a check for a job
// @Tags Jobs
// @Accept json
// @Param jobID path string true "Job ID"
// @Success 200 {object} string
// @Failure 400,500 {object} object
// @Router /trigger/{jobID} [get]
func handlerTriggerCheckJob(w http.ResponseWriter, r *http.Request) {
	enableCors(&w)

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
