# Installation

## Runner

Make the `runner/runner.sh` executable

```bash
chmod +x runner/runner.sh
```

## Config

Edit the `runner/config.sh` file and set the API_ENDPOINT and `API_KEY`

## Crontab

Wrap all your crontab commands with the `runner/runner.sh` script

```bash
crontab -e

# Example
* * * * * /home/runner/runner.sh testjob echo "hello world"
```

## Environment variables

Copy and edit the `.env.example` file to `.env` and adjust the variables to your needs.

```bash
cp example.env .env
```

Refer to the [Environment variables](environment-variables) section for more information.

## Jobs

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
