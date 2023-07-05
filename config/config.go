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
	API_KEY       string
	SMTP_HOST     string
	SMTP_PORT     string
	SMTP_USERNAME string
	SMTP_PASSWORD string
	SMTP_FROM     string
	SMTP_TO       string
	JOBS          map[string]Job
	DEBUG         bool
}

type Job struct {
	JobID     string   `json:"job_id"`
	Cron      string   `json:"cron"`
	MinTime   Duration `json:"min_time"`   // In seconds
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
	c.SMTP_HOST = os.Getenv("SMTP_HOST")
	c.SMTP_PORT = os.Getenv("SMTP_PORT")
	c.SMTP_USERNAME = os.Getenv("SMTP_USERNAME")
	c.SMTP_PASSWORD = os.Getenv("SMTP_PASSWORD")
	c.SMTP_FROM = os.Getenv("SMTP_FROM")
	c.SMTP_TO = os.Getenv("SMTP_TO")
	c.DEBUG = os.Getenv("DEBUG") == "true" || os.Getenv("DEBUG") == "1" || os.Getenv("DEBUG") == "TRUE"
	log.Info("DEBUG: ", c.DEBUG)
	if !c.ValideForMailEnabled() {
		log.Warn("Mail is not enabled")
	}
	// Jobs (from env with prefix JOB_)
	// environ := os.Environ()
	// c.JOBS = make(map[string]Job)
	// if c.DEBUG {

	// 	log.Info("Parsing Jobs:")
	// }
	// for _, env := range environ {
	// 	// JOB_jobid_gracetime = "* 0 * * *"
	// 	// Example: JOB_1234567890_1h = "* 0 * * *"
	// 	// log.Info(env)
	// 	PREFIX := "JOB_"
	// 	if len(env) > len(PREFIX) && env[:len(PREFIX)] == PREFIX {
	// 		if c.DEBUG {
	// 			log.Info("Found Job: " + env)
	// 		}
	// 		// Remove prefix
	// 		env = env[len(PREFIX):]
	// 		// Split by _
	// 		parts := strings.Split(env, "_")
	// 		if len(parts) != 2 {
	// 			log.Error("Invalid Job: " + env)
	// 			continue
	// 		}

	// 		// Parse grace_time
	// 		// Cut at =
	// 		cron := strings.Split(parts[1], "=")[1]
	// 		parts[1] = strings.Split(parts[1], "=")[0]

	// 		// Parse duration
	// 		graceTime, err := time.ParseDuration(parts[1])
	// 		if err != nil {
	// 			log.Error("Invalid duration: " + parts[1])
	// 			continue
	// 		}

	// 		// Add to map
	// 		c.JOBS[parts[0]] = Job{
	// 			JobID:     parts[0],
	// 			Cron:      cron,
	// 			GraceTime: Duration{graceTime},
	// 		}
	// 	}
	// }

	c.InitFromFile()
	// if c.DEBUG {
	// 	log.Info("Jobs from file:")
	// 	log.Info(c.JOBS)
	// 	for _, job := range c.JOBS {
	// 		log.Info(job)
	// 	}

	// }
}

// Jobs from config file (jobs.json)
func (c *Config) InitFromFile() {
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

	// Example:
	// {
	// 	"1234567890": {
	// 		"cron": "* 0 * * *",
	// 		"grace_time": "1h"
	// 	}
	// }

	var jobs map[string]Job
	err = json.Unmarshal(byteValue, &jobs)
	if err != nil {
		log.Error(err)
		return
	}
	// Check if grace_time is lower than min_time
	for _, job := range jobs {
		if job.GraceTime.Duration < job.MinTime.Duration {
			log.Error("GraceTime is lower than MinTime for job: " + job.JobID)
			log.Error("Please fix your jobs.json file")
			return
		}
	}

	c.JOBS = jobs

}
