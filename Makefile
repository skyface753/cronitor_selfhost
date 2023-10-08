debug-python:
	APIKEY=apikey123 \
	DEV=true \
	MONGODB_CONNECTION_URI="mongodb://admin:admin@127.0.0.1:27017/jobs_db_dev?authSource=admin" \
	python3 -m server

run-cronrunner:
	APIKEY=apikey123 \
	DEV=true \
	python3 -m server.cronrunner

prisma:
	prisma generate --schema ./server/prisma/schema.prisma
	prisma db push --schema ./server/prisma/schema.prisma