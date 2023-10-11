# Conitor Self-Hosted

Cronitor is a monitoring platform for your cron jobs, background tasks and scheduled scripts.

This Repository is a self-developed, self-hosted version of Cronitor by [Skyface](https://skyface.de).

## Installation

### Runner

Make the `scripts/runner.sh` executable

```bash
chmod +x scripts/runner.sh
```

### Config

Edit the `scripts/config.sh` file and set the API_ENDPOINT and `API_KEY` (same as in the `.env` file).

### Jobs

The server needs a `jobs.json` file to know which jobs to run.

#### Automatically

Use the `scripts/job_generator.sh` script to generate the `jobs.json` file.

It will read your crontabs and asks you for a name and grace time for each job.

```bash
chmod +x scripts/job_generator.sh
./scripts/job_generator.sh
```

> **NOTE** Names must be unique and can only contain letters, numbers and underscores (No spaces are allowed).
> **NOTE** The grace time is in seconds. If the job runs longer than the grace time it will be marked as failed.

#### Manually

Fill the `jobs.json` with your cronjobs.

For the above crontab example the `jobs.json` should look like this:

```json
[
  "testjob": {
    "cron": "* * * * *",
    "grace_time": "60"
  }
]
```

> Note: The `grace_time` is the time in seconds the job is allowed to run. If the job runs longer than the `grace_time` it will be marked as failed.

### Crontab

Wrap all your crontab commands with the `scripts/runner.sh` script

```bash
crontab -e

# Example
* * * * * /home/user/cronitor_selfhost/scripts/runner.sh testjob echo "hello world"
```

### Start the server

```bash
docker-compose up -d --build
```

### Environment variables

Copy and edit the `.env.example` file to `.env` and adjust the variables to your needs.

```bash
cp example.env .env
```

| Variable            | Description                                                        | Required               | Default     |
| ------------------- | ------------------------------------------------------------------ | ---------------------- | ----------- |
| APIKEY              | The API key to inject results (same as in the `scripts/config.sh`) | true                   |             |
| CLIENT_URL          | The url of the frontend (for cors)                                 | false                  | [SAME-SITE] |
| DATABASE_URL        | The url of the postgres database (like in the docker-compose.yml)  | true                   |             |
| NOTIFY_DISCORD      | Enable Discord notifications                                       | false                  | false       |
| NOTIFY_MAIL         | Enable mail notifications                                          | false                  | false       |
| NOTIFY_SLACK        | Enable Slack notifications                                         | false                  | false       |
| DISCORD_WEBHOOK_URL | The Discord webhook url                                            | IF NOTIFY_DISCORD=true |             |
| SLACK_WEBHOOK_URL   | The Slack webhook url                                              | IF NOTIFY_SLACK=true   |             |
| SMTP_HOST           | The SMTP host                                                      | IF NOTIFY_DISCORD=true |             |
| SMTP_PORT           | The SMTP port                                                      | IF NOTIFY_DISCORD=true |             |
| SMTP_USERNAME       | The SMTP username                                                  | IF NOTIFY_DISCORD=true |             |
| SMTP_PASSWORD       | The SMTP password                                                  | IF NOTIFY_DISCORD=true |             |
| SMTP_FROM           | The sender address of the emails                                   | IF NOTIFY_DISCORD=true |             |
| SMTP_TO             | The receiver address of the emails                                 | IF NOTIFY_DISCORD=true |             |
| SHOW_DOCS           | Show the docs at /api/v1/docs and /api/v1/redocs                   | false                  | false       |

## Features

- [x] Self-hosted
- [x] Email notifications
  - [x] Failed
  - [x] Expired
  - [x] Resolved
- [x] Webhook notifications
  - [x] Discord
  - [x] Slack
- [x] Web UI
- [x] API (with [Docs and Redocs](environment-variables))
- [x] Database
  - [x] Postgres
  - [] Usage for multi instances

## TODO

## Delete Jobs

The jobs are stored in the database.
So it is not enough to delete the job from the `jobs.json`.

Steps:

- Delete the job from the `jobs.json`
- Restart the server
- Run the `scripts/delete_job.sh` script

```bash
./scripts/delete_job.sh # You will receive a list of all jobs and can select the job you want to delete.
```

### Delete a job - Example

Remove the job `testjob` from the `jobs.json`.

```bash
nano jobs.json
# Remove the job "testjob"
```

Restart the server

```bash
docker-compose restart
```

Wait a few seconds and run the `scripts/delete_job.sh` script.

```bash
./scripts/delete_job.sh
```

Enter the job id you want to delete and press enter.

Example output:

```bash
cronitor_selfhost git:(main) ✗ ./scripts/delete_job.sh
Disabled jobs:

testjob

Enter job id to delete: testjob
{"message":"Job deleted"}
```
