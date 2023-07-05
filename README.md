make the runner/runner.sh executable

```bash
chmod +x runner/runner.sh
```

wrap all your crontab commands with the runner/runner.sh script

```bash
crontab -e
* * * * * /path/to/runner/runner.sh jobname <Command> # Example * * * * * /home/runner/runner.sh testjob echo "hello world"
```

Copy and edit the `example.env` file to `.env` and add your jobs to the `docker-compose.yml` environment variables.

```bash
cp example.env .env
```

Edit the `.env` file. Set the SMTP variables to your SMTP server. The `FROM` variable is the sender address of the emails.
<br>
Now add your jobs to the `docker-compose.yml` environment variables.
The syntax is `JOB_<jobname>_<grace_time>`. You can use all possible [go time formats](https://pkg.go.dev/time#ParseDuration) like `10s` or `1m` for the grace time.
The Value of the environment variable is the cron schedule. It should be the same as the one you used in the crontab, so the `* * * * *` in this example.
For the `testjob` from above it would look like this:

`docker-compose.yml` example:

```yaml
services:
  server:
    image: skyface753/skycron-server
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - '8080:8080'
    environment:
      JOB_jobname_10s: '* * * * *'
```
