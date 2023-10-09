debug-python:
	APIKEY=apikey123 \
	DEV=true \
	DATABASE_URL="postgresql://root:root@localhost:5432/test_db" \
	python3 -m server

run-cronrunner:
	APIKEY=apikey123 \
	DEV=true \
	DATABASE_URL="postgresql://root:root@localhost:5432/test_db" \
	python3 -m server.cronrunner

prisma:
	prisma generate --schema ./server/prisma/schema.prisma
	DATABASE_URL="postgresql://root:root@localhost:5432/test_db" \
	prisma db push --schema ./server/prisma/schema.prisma

test: prisma
	pytest server -s