swag-api-doc:
	swag init --parseDependency

debug: 
	API_KEY=apikey123 \
	MAIL_DISABLED=true \
	INFLUXDB_USERNAME=my-user \
	INFLUXDB_PASSWORD=my-password \
	INFLUXDB_ORG=my-org \
	INFLUXDB_BUCKET=my-bucket \
	INFLUXDB_ADMIN_TOKEN=my-token \
	DEBUG=true \
	go run .

debug-python:
	MAIL_DISABLED=true \
	APIKEY=apikey123 \
	DEV=true \
	python3 -m server