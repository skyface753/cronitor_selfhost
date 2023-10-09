#!/bin/bash
# /bin/bash
prisma generate --schema ./server/prisma/schema.prisma
prisma db push --schema ./server/prisma/schema.prisma

python -m server.cronrunner &
python -m server