package mail

import (
	"net/smtp"

	log "github.com/sirupsen/logrus"
	"github.com/skyface753/cronitor_selfhost/config"
)

func Send(config config.Config, job_id string, output string, result bool) bool {
	// Check if all the required fields are set
	if config.SMTP_HOST == "" || config.SMTP_PORT == "" || config.SMTP_FROM == "" || config.SMTP_TO == "" {
		log.Error("SMTP_HOST, SMTP_PORT, SMTP_FROM and SMTP_TO must be set")
		// Return an error
		return false
	}
	// Send mail
	from := config.SMTP_FROM
	pass := config.SMTP_PASSWORD

	to := []string{config.SMTP_TO}

	msg := "From: " + from + "\n" +
		"To: " + config.SMTP_TO + "\n"
	if result {
		msg += "Subject: Cronitor job " + job_id + " succeeded\n\n"
	} else {
		msg += "Subject: Cronitor job " + job_id + " failed\n\n"
	}
	msg += "Log output:\n" + output + "\n"

	err := smtp.SendMail(config.SMTP_HOST+":"+config.SMTP_PORT,
		smtp.PlainAuth("", from, pass, config.SMTP_HOST),
		from, to, []byte(msg))

	return err == nil
}
