package config

func (c *Config) ValideForMailEnabled() bool {
	return c.SMTP_HOST != "" && c.SMTP_PORT != "" && c.SMTP_FROM != "" && c.SMTP_TO != ""
}

func (c *Config) JobExists(job_id string) bool {
	_, ok := c.JOBS[job_id]
	return ok
}
