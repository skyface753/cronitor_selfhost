# Conitor Self-Hosted

Cronitor is a monitoring platform for your cron jobs, background tasks and scheduled scripts.

This Repository is a self-developed, self-hosted version of Cronitor by [Skyface](https://skyface.de).

## Installation

### Runner

Make the `runner/runner.sh` executable

```bash
chmod +x runner/runner.sh
```

### Config

Edit the `runner/config.sh` file and set the API_ENDPOINT and `API_KEY`

### Crontab

Wrap all your crontab commands with the `runner/runner.sh` script

```bash
crontab -e

# Example
* * * * * /home/runner/runner.sh testjob echo "hello world"
```

### Environment variables

Copy and edit the `.env.example` file to `.env` and adjust the variables to your needs.

```bash
cp example.env .env
```

| Variable               | Description                                                              | Required                   | Default                                                            |
| ---------------------- | ------------------------------------------------------------------------ | -------------------------- | ------------------------------------------------------------------ |
| APIKEY                 | The API key to inject results                                            | true                       |                                                                    |
| CLIENT_URL             | The url of the frontend (for cors)                                       | false                      | [SAME-SITE]                                                        |
| MONGODB_CONNECTION_URI | The MongoDB connection URI                                               | false                      | mongodb://admin:admin@127.0.0.1:27017/jobs_db_dev?authSource=admin |
| DB_NAME                | The MongoDB database name (should be the same as MONGODB_CONNECTION_URI) | false                      | jobs_db_dev                                                        |
| COLL_NAME              | The MongoDB collection name                                              | false                      | job_results                                                        |
| NOTIFY_PROVIDER        | The notification provider (mail or discord)                              | false                      | None                                                               |
| DISCORD_WEBHOOK_URL    | The Discord webhook url                                                  | IF NOTIFY_PROVIDER=discord |                                                                    |
| SMTP_HOST              | The SMTP host                                                            | IF NOTIFY_PROVIDER=mail    |                                                                    |
| SMTP_PORT              | The SMTP port                                                            | IF NOTIFY_PROVIDER=mail    |                                                                    |
| SMTP_USERNAME          | The SMTP username                                                        | IF NOTIFY_PROVIDER=mail    |                                                                    |
| SMTP_PASSWORD          | The SMTP password                                                        | IF NOTIFY_PROVIDER=mail    |                                                                    |
| SMTP_FROM              | The sender address of the emails                                         | IF NOTIFY_PROVIDER=mail    |                                                                    |
| SMTP_TO                | The receiver address of the emails                                       | IF NOTIFY_PROVIDER=mail    |                                                                    |
| SHOW_DOCS              | Show the docs at /api/v1/docs and /api/v1/redocs                         | false                      | false                                                              |

### Jobs

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

## Features

- [x] Self-hosted
- [x] Email notifications
  - [x] Failed
  - [x] Expired
  - [x] Resolved
- [x] Webhook notifications
  - [x] Discord
- [x] Web UI
- [x] API (with [Docs and Redocs](environment-variables))

## TODO

- [ ] Webhook notifications
  - [ ] Slack
  - [ ] Telegram
