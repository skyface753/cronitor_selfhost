package config

import (
	"encoding/json"
	"fmt"
	"io"
	"os"
	"time"

	log "github.com/sirupsen/logrus" // Use default log, because the log wrapper is not initialized yet
)

type Config struct {
	API_KEY              string
	MAIL_DISABLED         bool
	SMTP_HOST            string
	SMTP_PORT            string
	SMTP_USERNAME        string
	SMTP_PASSWORD        string
	SMTP_FROM            string
	SMTP_TO              string
	INFLUXDB_ORG         string
	INFLUXDB_BUCKET      string
	INFLUXDB_ADMIN_TOKEN string
	JOBS                 map[string]Job
	DEBUG                bool
}

type Job struct {
	JobID     string   `json:"job_id"`
	Cron      string   `json:"cron"`
	GraceTime Duration `json:"grace_time"` // In seconds
}
type Duration struct {
	time.Duration
}

func (duration *Duration) UnmarshalJSON(b []byte) error {
	var unmarshalledJson interface{}

	err := json.Unmarshal(b, &unmarshalledJson)
	if err != nil {
		return err
	}

	switch value := unmarshalledJson.(type) {
	case float64:
		duration.Duration = time.Duration(value)
	case string:
		duration.Duration, err = time.ParseDuration(value)
		if err != nil {
			return err
		}
	default:
		return fmt.Errorf("invalid duration: %#v", unmarshalledJson)
	}

	return nil
}

// From environment variables
func (c *Config) Init() {
	c.API_KEY = os.Getenv("API_KEY")
	c.MAIL_DISABLED = os.Getenv("MAIL_DISABLED") == "true" 
	c.SMTP_HOST = os.Getenv("SMTP_HOST")
	c.SMTP_PORT = os.Getenv("SMTP_PORT")
	c.SMTP_USERNAME = os.Getenv("SMTP_USERNAME")
	c.SMTP_PASSWORD = os.Getenv("SMTP_PASSWORD")
	c.SMTP_FROM = os.Getenv("SMTP_FROM")
	c.SMTP_TO = os.Getenv("SMTP_TO")
	c.INFLUXDB_ORG = os.Getenv("INFLUXDB_ORG")
	c.INFLUXDB_BUCKET = os.Getenv("INFLUXDB_BUCKET")
	c.INFLUXDB_ADMIN_TOKEN = os.Getenv("INFLUXDB_ADMIN_TOKEN")
	c.DEBUG = os.Getenv("DEBUG") == "true" || os.Getenv("DEBUG") == "1" || os.Getenv("DEBUG") == "TRUE"
	log.Info("DEBUG: ", c.DEBUG)
	if !c.ValideForMailEnabled() {
		log.Warn("Mail is not enabled")
	}

	c.ReadJobsJSON()

}

// Jobs from config file (jobs.json)
func (c *Config) ReadJobsJSON() {
	jsonFile, err := os.Open("/jobs.json")
	if err != nil {
		log.Error(err)
		return
	}
	defer jsonFile.Close()

	// Read file
	byteValue, err := io.ReadAll(jsonFile)
	if err != nil {
		log.Error(err)
		return
	}

	// Parse json
	var jobs map[string]Job
	err = json.Unmarshal(byteValue, &jobs)
	if err != nil {
		log.Error(err)
		return
	}
	// Jobid as key
	for jobid, job := range jobs {
		job.JobID = jobid
		jobs[jobid] = job
	}

	// Check if grace_time is lower than min_time
	for _, job := range jobs {
		// Check if all values are set
		if job.Cron == "" {
			log.Error("Cron is empty for job: " + job.JobID)
			log.Error("Please fix your jobs.json file")
			return
		}

		if job.JobID == "" {
			log.Error("JobID is empty for job: " + job.JobID)
			log.Error("Please fix your jobs.json file")
			return
		}

		if job.GraceTime.Duration < 0 {
			log.Error("GraceTime is negative for job: " + job.JobID)
			log.Error("Please fix your jobs.json file")
			return
		}

	}

	c.JOBS = jobs

}

func (c *Config) GetJob(jobID string) *Job {
	job, ok := c.JOBS[jobID]
	if !ok {
		return nil
	}
	return &job
}
