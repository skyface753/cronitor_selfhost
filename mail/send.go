package mail

import (
	"net/smtp"

	// log "github.com/sirupsen/logrus"
	"github.com/skyface753/cronitor_selfhost/config"
	log "github.com/skyface753/cronitor_selfhost/skyLog"
)

func Send(config config.Config, job_id string, output string, result bool) {
	if config.MAIL_DISABLED {
		return
	}
	// Check if all the required fields are set
	if !config.ValideForMailEnabled() {
		log.Info("SMTP_HOST, SMTP_PORT, SMTP_FROM and SMTP_TO must be set")
		return
	}
	// Send mail
	from := config.SMTP_FROM
	pass := config.SMTP_PASSWORD

	to := []string{config.SMTP_TO}

	msg := "From: " + from + "\n" +
		"To: " + config.SMTP_TO + "\n"
	if result {
		msg += "Subject: [SUCCESS] Cronitor job " + job_id + " succeeded\n\n"
	} else {
		msg += "Subject: [FAILURE] Cronitor job " + job_id + " failed\n\n"
	}
	msg += "Log output:\n" + output + "\n"

	err := smtp.SendMail(config.SMTP_HOST+":"+config.SMTP_PORT,
		smtp.PlainAuth("", from, pass, config.SMTP_HOST),
		from, to, []byte(msg))

	// return err == nil
	if err != nil {
		log.Error(err)
	}
}
