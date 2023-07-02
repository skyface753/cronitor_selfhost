package config

import (
	"os"
	"strings"
	"time"

	log "github.com/sirupsen/logrus"
)

type Config struct {
	API_KEY       string
	SMTP_HOST     string
	SMTP_PORT     string
	SMTP_USERNAME string
	SMTP_PASSWORD string
	SMTP_FROM     string
	SMTP_TO       string
	TRIGGERS      map[string]Trigger
}

type Trigger struct {
	JobID string `json:"job_id"`
	// Time, when the job should be triggered
	// TriggerAt time.Time     `json:"trigger_at"`
	Cron      string        `json:"cron"`
	GraceTime time.Duration `json:"grace_time"` // In seconds
}

// From environment variables
func (c *Config) FromEnv() {
	c.API_KEY = os.Getenv("API_KEY")
	log.Info("API_KEY: " + c.API_KEY)
	c.SMTP_HOST = os.Getenv("SMTP_HOST")
	c.SMTP_PORT = os.Getenv("SMTP_PORT")
	c.SMTP_USERNAME = os.Getenv("SMTP_USERNAME")
	c.SMTP_PASSWORD = os.Getenv("SMTP_PASSWORD")
	c.SMTP_FROM = os.Getenv("SMTP_FROM")
	c.SMTP_TO = os.Getenv("SMTP_TO")
	// Triggers (from env with prefix TRIGGER_)
	environ := os.Environ()
	c.TRIGGERS = make(map[string]Trigger)
	log.Info("TRIGGERS:")
	for _, env := range environ {
		// TRIGGER_jobid_gracetime = "* 0 * * *"
		// Example: TRIGGER_1234567890_1h = "* 0 * * *"
		// log.Info(env)
		if len(env) > 8 && env[:8] == "TRIGGER_" {
			log.Info("Found trigger: " + env)
			// Remove prefix
			env = env[8:]
			// Split by _
			parts := strings.Split(env, "_")
			if len(parts) != 2 {
				log.Error("Invalid trigger: " + env)
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
			c.TRIGGERS[parts[0]] = Trigger{
				JobID:     parts[0],
				Cron:      cron,
				GraceTime: graceTime,
			}
		}
	}

}
