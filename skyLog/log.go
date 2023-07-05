package log

import (
	log "github.com/sirupsen/logrus"
	"github.com/skyface753/cronitor_selfhost/config"
)

var configClient *config.Config

func Init(config *config.Config) {
	configClient = config
}

func logToConsole(logLevel log.Level, args ...interface{}) {
	if configClient.DEBUG {
		return
	}
	switch logLevel {
	case log.DebugLevel:
		log.Debug(args...)
	case log.InfoLevel:
		log.Info(args...)
	case log.ErrorLevel:
		log.Error(args...)
	case log.FatalLevel:
		log.Fatal(args...)
	}
}

func Debug(args ...interface{}) {
	logToConsole(log.DebugLevel, args...)
}

func Info(args ...interface{}) {
	logToConsole(log.InfoLevel, args...)
}

func Error(args ...interface{}) {
	logToConsole(log.ErrorLevel, args...)
}

func Fatal(args ...interface{}) {
	logToConsole(log.FatalLevel, args...)
}
