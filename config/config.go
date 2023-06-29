package config

import (
	"os"

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
}
