package config

import (
	"os"
	"strings"
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
	JobID     string        `json:"job_id"`
	Cron      string        `json:"cron"`
	GraceTime time.Duration `json:"grace_time"` // In seconds
}

// From environment variables
func (c *Config) FromEnv() {
	c.API_KEY = os.Getenv("API_KEY")
	c.SMTP_HOST = os.Getenv("SMTP_HOST")
	c.SMTP_PORT = os.Getenv("SMTP_PORT")
	c.SMTP_USERNAME = os.Getenv("SMTP_USERNAME")
	c.SMTP_PASSWORD = os.Getenv("SMTP_PASSWORD")
	c.SMTP_FROM = os.Getenv("SMTP_FROM")
	c.SMTP_TO = os.Getenv("SMTP_TO")
	c.DEBUG = os.Getenv("DEBUG") == "true" || os.Getenv("DEBUG") == "1" || os.Getenv("DEBUG") == "TRUE"
	if !c.ValideForMailEnabled() {
		log.Warn("Mail is not enabled")
	}
	// Jobs (from env with prefix JOB_)
	environ := os.Environ()
	c.JOBS = make(map[string]Job)
	if c.DEBUG {

		log.Info("Parsing Jobs:")
	}
	for _, env := range environ {
		// JOB_jobid_gracetime = "* 0 * * *"
		// Example: JOB_1234567890_1h = "* 0 * * *"
		// log.Info(env)
		PREFIX := "JOB_"
		if len(env) > len(PREFIX) && env[:len(PREFIX)] == PREFIX {
			if c.DEBUG {
				log.Info("Found Job: " + env)
			}
			// Remove prefix
			env = env[len(PREFIX):]
			// Split by _
			parts := strings.Split(env, "_")
			if len(parts) != 2 {
				log.Error("Invalid Job: " + env)
				continue
			}

			// Parse grace_time
			// Cut at =
			cron := strings.Split(parts[1], "=")[1]
			parts[1] = strings.Split(parts[1], "=")[0]

			// Parse duration
			graceTime, err := time.ParseDuration(parts[1])
			if err != nil {
				log.Error("Invalid duration: " + parts[1])
				continue
			}

			// Add to map
			c.JOBS[parts[0]] = Job{
				JobID:     parts[0],
				Cron:      cron,
				GraceTime: graceTime,
			}
		}
	}

}
