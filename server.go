package main

import (
	"context"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/gorilla/mux"
	// log "github.com/sirupsen/logrus"
	"github.com/skyface753/cronitor_selfhost/config"
	"github.com/skyface753/cronitor_selfhost/influx"
	"github.com/skyface753/cronitor_selfhost/mail"
	log "github.com/skyface753/cronitor_selfhost/skyLog"

	//	"github.com/mileusna/crontab"
)

// Coming from the runner.sh script to the /api/v1/cron/result endpoint
type CronJobResult struct {
	JobID   string `json:"job_id"`
	ApiKey  string `json:"api_key"`
	Error   string `json:"error"`
	Success bool   `json:"success"`
}

var (
	influxClient *influx.Influx
	configClient *config.Config
	waitingJobs  []config.Job
)

func missingJob(jobID string, graceTime time.Duration) {
	mail.Send(*configClient, jobID, "Job is missing", false)
	influxClient.InsertUptimeMissing(context.Background(), configClient, jobID, graceTime)
}

func failedJob(jobID string, content string) {
	mail.Send(*configClient, jobID, content, false)
	influxClient.InsertUptime(context.Background(), configClient, jobID, false, content)
}

func successJob(jobID string) {
	influxClient.InsertUptime(context.Background(), configClient, jobID, true, "")
}

func removeJobFromWaiting(jobID string) {
	for i, job := range waitingJobs {
		if job.JobID == jobID {
			// Fix error: panic: runtime error: slice bounds out of range [3:1]
			if i == 0 {
				waitingJobs = waitingJobs[1:]
			} else if i == len(waitingJobs)-1 {
				waitingJobs = waitingJobs[:i]
			} else {
				waitingJobs = append(waitingJobs[:i], waitingJobs[i+1:]...)
			}
			return
		}
	}
}

func checkIsJobWaiting(jobID string) bool {
	for _, job := range waitingJobs {
		if job.JobID == jobID {
			return true
		}
	}
	return false
}

func checkService(job *config.Job) {
	// Add job to waiting jobs
	waitingJobs = append(waitingJobs, *job)
	log.Info(job.JobID, "Job added to waiting jobs")
	time.Sleep(5 * time.Second)
	if job.GraceTime.Duration == 0 {
		log.Info("This doesnt make sense LOL - But ok")
		if checkIsJobWaiting(job.JobID) {
			log.Info("Job is waiting - send mail, log it and remove from waiting")
			missingJob(job.JobID, job.GraceTime.Duration)
			removeJobFromWaiting(job.JobID)
		} else {
			log.Info("Job is not waiting - everything is ok")
		}
		return
	}

	go func() {
		time.Sleep(job.GraceTime.Duration)
		if checkIsJobWaiting(job.JobID) {
			log.Info("Job is still waiting AFTER GRACE TIME - send mail, log it and remove from waiting")
			missingJob(job.JobID, job.GraceTime.Duration)
			removeJobFromWaiting(job.JobID)
		} else {
			log.Info("Job is not waiting AFTER GRACE TIME - everything is ok")
		}
	}()
}

func main() {
	// Create a new router
	r := mux.NewRouter()
	addr := "127.0.0.1:8080"
	if os.Getenv("PRODUCTION") == "true" {
		addr = "0.0.0.0:8080"
	}
	// Create a new server
	srv := &http.Server{
		Handler:      r,
		Addr:         addr,
		WriteTimeout: 15 * time.Second,
		ReadTimeout:  15 * time.Second,
	}
	configClient = &config.Config{}
	configClient.Init()
	log.Init(configClient)
	influxClient = influx.NewInflux(configClient)

	r.HandleFunc("/api/v1/cron/status", handlerStatusAllFull).Methods("GET", "POST")

	r.HandleFunc("/api/v1/cron/status/last", handlerStatusAllLast).Methods("GET", "POST")

	r.HandleFunc("/api/v1/cron/status/job/{jobID}", handlerJobStatus).Methods("GET", "POST")

	r.HandleFunc("/api/v1/cron/status/waiting", handlerWaitingJobs).Methods("GET", "POST")

	r.HandleFunc("/api/v1/cron/result", handlerCronResult).Methods("POST", "GET")

	r.HandleFunc("/api/v1/trigger/{jobID}", handlerTriggerCheckJob).Methods("GET", "POST")

	// Start the server
	go func() {
		log.Info("Server started on port 8080")
		if err := srv.ListenAndServe(); err != nil {
			log.Fatal(err)
		}
	}()

	// Register Jobs
	// go func() {
	// 	log.Info("Registering jobs...")
	// 	for _, job := range configClient.JOBS {
	// 		log.Info("Registering job: ", job)
	// 		crontab.New().MustAddJob(job.Cron, checkService, &job)
	// 	}
	// }()

	// Graceful shutdown
	c := make(chan os.Signal, 1)
	signal.Notify(c, os.Interrupt, syscall.SIGTERM)
	<-c

	log.Info("Shutting down server...")

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	srv.Shutdown(ctx)
	log.Info("Server gracefully stopped")
}
