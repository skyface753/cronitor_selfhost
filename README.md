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

| Variable               | Description                                                              | Required               | Default                                                            |
| ---------------------- | ------------------------------------------------------------------------ | ---------------------- | ------------------------------------------------------------------ |
| APIKEY                 | The API key to inject results                                            | true                   |                                                                    |
| MAIL_DISABLED          | Disable sending emails (primarily for testing)                           | false                  | false                                                              |
| CLIENT_URL             | The url of the frontend (for cors)                                       | false                  | [SAME-SITE]                                                        |
| MONGODB_CONNECTION_URI | The MongoDB connection URI                                               | false                  | mongodb://admin:admin@127.0.0.1:27017/jobs_db_dev?authSource=admin |
| DB_NAME                | The MongoDB database name (should be the same as MONGODB_CONNECTION_URI) | false                  | jobs_db_dev                                                        |
| COLL_NAME              | The MongoDB collection name                                              | false                  | job_results                                                        |
| SMTP_HOST              | The SMTP host                                                            | IF MAIL_DISABLED=false |                                                                    |
| SMTP_PORT              | The SMTP port                                                            | IF MAIL_DISABLED=false |                                                                    |
| SMTP_USERNAME          | The SMTP username                                                        | IF MAIL_DISABLED=false |                                                                    |
| SMTP_PASSWORD          | The SMTP password                                                        | IF MAIL_DISABLED=false |                                                                    |
| SMTP_FROM              | The sender address of the emails                                         | IF MAIL_DISABLED=false |                                                                    |
| SMTP_TO                | The receiver address of the emails                                       | IF MAIL_DISABLED=false |                                                                    |
| SHOW_DOCS              | Show the docs at /api/v1/docs and /api/v1/redocs                         | false                  | false                                                              |

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
- [x] Web UI
- [x] API (with [Docs and Redocs](environment-variables))

## TODO

- [ ] Webhooks
