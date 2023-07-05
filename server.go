// http server listening on port 8080 with the following endpoints:
// - /api/v1/cron/afterrun

package main

import (
	"context"
	"encoding/json"
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

	"github.com/mileusna/crontab"
)

type Result struct {
	JobID   string `json:"job_id"`
	ApiKey  string `json:"api_key"`
	Error   string `json:"error"`
	Success bool   `json:"success"`
}

type Trigger struct {
	JobID     string        `json:"job_id"`
	ApiKey    string        `json:"api_key"`
	GraceTime time.Duration `json:"grace_time"` // In seconds
}

var (
	influxClient *influx.Influx
	configClient *config.Config
)

func checkService(jobID string, minTime *config.Duration, graceTime *config.Duration) (bool, error) {
	// Wait for min time
	if minTime != nil {
		log.Info(jobID, "Waiting for min time")
		time.Sleep(time.Duration(minTime.Duration))
		log.Info(jobID, "Min time is over")
	}
	// Read from influx
	success, content, err := influxClient.Read(context.Background(), configClient, jobID, time.Minute)
	if err != nil {
		log.Error(err)
		return false, err
	}

	log.Info("Job: ", jobID, " success: ", success, " content: ", content)
	log.Info("Real Grace time: ", graceTime)
	// Check if the job was successful
	if success {
		return true, nil
	}
	// Check if the grace time is null
	if graceTime == nil {

		log.Info(jobID, "Grace time is null => send alert")
		// Send alert
		mail.Send(*configClient, jobID, content, false)
		return false, nil
	}

	// Grace time is not over
	// TODO: register a new trigger
	log.Info(jobID, "Grace time is not over")
	// gracetime - mintime
	newGraceTime := graceTime.Duration - minTime.Duration

	// log.Info(time.Now().Add(-*graceTime))
	go func() {
		// Wait for grace time
		log.Info(jobID, "Waiting for new grace time:", newGraceTime)
		// time.Sleep(*graceTime)
		// config.Duration to time.Duration
		time.Sleep(newGraceTime)
		log.Info(jobID, "After grace time => recheck")
		checkService(jobID, nil, nil)
	}()
	return true, nil

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
	influxClient = influx.NewInflux()

	r.HandleFunc("/api/v1/cron/status", func(w http.ResponseWriter, r *http.Request) {
		// json.NewEncoder(w).Encode(configClient.JOBS)
		result, err := influxClient.GetAllForAll(context.Background())
		if err != nil {
			log.Error(err)
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}
		json.NewEncoder(w).Encode(result)
	})

	r.HandleFunc("/api/v1/cron/status/last", func(w http.ResponseWriter, r *http.Request) {
		result, err := influxClient.GetAllLastForAllJobs(context.Background(), configClient)
		if err != nil {
			log.Error(err)
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}
		json.NewEncoder(w).Encode(result)
	})

	r.HandleFunc("/api/v1/cron/status/job/{jobID}", func(w http.ResponseWriter, r *http.Request) {
		vars := mux.Vars(r)
		jobID := vars["jobID"]
		result, err := influxClient.GetAllForJob(context.Background(), configClient, jobID)
		if err != nil {
			log.Error(err)
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}
		json.NewEncoder(w).Encode(result)
	})

	r.HandleFunc("/api/v1/cron/result", func(w http.ResponseWriter, r *http.Request) {
		var result Result
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
			mail.Send(*configClient, result.JobID, result.Error, result.Success)
		}
		// Write to influx
		err = influxClient.InsertUptime(context.Background(), configClient, result.JobID, result.Success, result.Error)
		if err != nil {
			log.Error(err)
			http.Error(w, "Writing to influx failed", http.StatusInternalServerError)
			return
		}
		// fmt.Fprintf(w, "Hello, %q", r.URL.Path)
	})

	// Start the server
	go func() {
		log.Info("Server started on port 8080")
		if err := srv.ListenAndServe(); err != nil {
			log.Fatal(err)
		}
	}()

	// Register Jobs
	go func() {

		log.Info("Registering jobs...")
		for _, job := range configClient.JOBS {
			log.Info("Registering job: ", job)
			crontab.New().MustAddJob(job.Cron, checkService, job.JobID, &job.MinTime, &job.GraceTime)
			// checkService(job.JobID, nil, nil)
			// checkService(influx, trigger.JobID, &trigger.GraceTime, &config)
		}
	}()

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
