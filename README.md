make the runner/runner.sh executable

```bash
chmod +x runner/runner.sh
```

Edit the `runner/config.sh` file and set the API_ENDPOINT and API_KEY
<br><br>
Then wrap all your crontab commands with the runner/runner.sh script

```bash
crontab -e
* * * * * /path/to/runner/runner.sh jobname <Command> # Example * * * * * /home/runner/runner.sh testjob echo "hello world"
```

Copy and edit the `.env.example` file to `.env` and add your jobs to the `docker-compose.yml` environment variables.

```bash
cp example.env .env
```

Edit the `.env` file. Set the SMTP variables to your SMTP server. The `FROM` variable is the sender address of the emails.
<br><br>
Now add jor jobs to the jobs.json
