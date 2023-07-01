cron as trigger (microservice)
it triggers the server which checks the service
if the service is down, the server registers a timer, which recheck the service after a grace time
