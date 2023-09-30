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

run-docker-debug:
	docker build -t skyface753/cronitor-server ./server
	docker run --rm -v ${PWD}/jobs.json:/jobs.json \
	-e APIKEY=apikey123 \
	-e MAIL_DISABLED=true \
	--network host \
	skyface753/cronitor-server