// http server listening on port 8080 with the following endpoints:
// - /api/v1/cron/afterrun

package main

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/gorilla/mux"
	log "github.com/sirupsen/logrus"
	"github.com/skyface753/cronitor_selfhost/config"
	"github.com/skyface753/cronitor_selfhost/influx"
	"github.com/skyface753/cronitor_selfhost/mail"

	"github.com/mileusna/crontab"
)

type Result struct {
	JobID   string `json:"job_id"`
	ApiKey  string `json:"api_key"`
	Output  string `json:"output"`
	Success bool   `json:"success"`
}

type Trigger struct {
	JobID     string        `json:"job_id"`
	ApiKey    string        `json:"api_key"`
	GraceTime time.Duration `json:"grace_time"` // In seconds
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
	config := config.Config{}
	config.FromEnv()
	influx := influx.NewInflux()

	r.HandleFunc("/api/v1/cron/trigger", func(w http.ResponseWriter, r *http.Request) {
		// Check if the api key is set
		var trigger Trigger
		err := json.NewDecoder(r.Body).Decode(&trigger)
		if err != nil {
			log.Error(err)
			http.Error(w, err.Error(), http.StatusBadRequest)
			return
		}
		if trigger.ApiKey != config.API_KEY {
			log.Error("Wrong api key")
			http.Error(w, "Wrong api key", http.StatusUnauthorized)
			return
		}
		// Check if the job id is set
		if trigger.JobID == "" {
			log.Error("JobID must be set")
			http.Error(w, "JobID must be set", http.StatusBadRequest)
			return
		}
		// Read from influx
		success, err := influx.Read(context.Background(), trigger.JobID, 1*time.Minute)
		if err != nil {
			log.Error(err)
			http.Error(w, "Reading from influx failed", http.StatusInternalServerError)
			return
		}
		log.Info(success)
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
		if result.ApiKey != config.API_KEY {
			log.Error("Wrong api key")
			http.Error(w, "Wrong api key", http.StatusUnauthorized)
			return
		}
		// Check if all the required fields are set
		if result.JobID == "" || result.Output == "" {
			log.Error("JobID and output must be set")
			http.Error(w, "JobID and output must be set", http.StatusBadRequest)
			return
		}
		if !result.Success {
			success := mail.Send(config, result.JobID, result.Output, result.Success)
			if !success {
				log.Error("Sending mail failed: ", success)
				http.Error(w, "Sending mail failed", http.StatusInternalServerError)
				return
			}
		}
		// Write to influx
		err = influx.InsertUptime(context.Background(), result.JobID, result.Success)
		if err != nil {
			log.Error(err)
			http.Error(w, "Writing to influx failed", http.StatusInternalServerError)
			return
		}
		fmt.Fprintf(w, "Hello, %q", r.URL.Path)
	})

	// Start the server
	go func() {
		log.Info("Server started on port 8080")
		if err := srv.ListenAndServe(); err != nil {
			log.Fatal(err)
		}
	}()

	// Triggers register
	go func() {
		log.Info("Registering triggers...")
		for _, trigger := range config.TRIGGERS {
			log.Info("Registering trigger: ", trigger)
			crontab.New().MustAddJob(trigger.Cron, func() {
				log.Info("Triggering job: ", trigger)
			})

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
