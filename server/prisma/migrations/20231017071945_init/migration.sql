-- CreateEnum
CREATE TYPE "JobRunResult" AS ENUM ('SUCCESS', 'FAILED', 'EXPIRED');

-- CreateTable
CREATE TABLE "Job" (
    "id" TEXT NOT NULL,
    "cron" TEXT NOT NULL,
    "grace_time" INTEGER NOT NULL,
    "is_waiting" BOOLEAN NOT NULL,
    "is_running" BOOLEAN NOT NULL,
    "has_failed" BOOLEAN NOT NULL,
    "has_expired" BOOLEAN NOT NULL DEFAULT false,
    "enabled" BOOLEAN NOT NULL,

    CONSTRAINT "Job_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "JobRun" (
    "id" SERIAL NOT NULL,
    "job_id" TEXT NOT NULL,
    "started_at" TIMESTAMP(3) NOT NULL,
    "finished_at" TIMESTAMP(3) NOT NULL,
    "result" "JobRunResult" NOT NULL,
    "command" TEXT NOT NULL,
    "output" TEXT,
    "runtime" INTEGER NOT NULL,

    CONSTRAINT "JobRun_pkey" PRIMARY KEY ("id")
);

-- AddForeignKey
ALTER TABLE "JobRun" ADD CONSTRAINT "JobRun_job_id_fkey" FOREIGN KEY ("job_id") REFERENCES "Job"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
