#!/bin/bash


# Load the API endpoint and API key from the source file
# TODO: Make this configurable
# source /etc/cron-runner/config.sh
MYDIR="$(dirname "$(realpath "$0")")"
source "$MYDIR/config.sh"

JOB_ID=$1
# Shift the positional parameters to the left by 1 to get the command to run
shift

# Get the command to run from the arguments passed to the script
#!/bin/sh
C=''
for i in "$@"; do
    case "$i" in
        *\'*)
            i=`printf "%s" "$i" | sed "s/'/'\"'\"'/g"`
            ;;
        *) : ;;
    esac
    C="$C '$i'"
done
# Run the command and store the output, store stdout and stderr in different variables

BOOL="true"
if output=$(eval $C 2>&1 >/dev/null); then
    echo "Command succeeded"
    BOOL="true"
else
    echo "Command failed"
    BOOL="false"
fi

# Remove all newlines from the output
ERROR=$(echo "${output}" | tr -d '\n')
# Remove quotes
ERROR=$(echo "${ERROR}" | tr -d '"')
# Remove backslashes
ERROR=$(echo "${ERROR}" | tr -d '\\')

#sleep 5
echo $ERROR
API_RUNNER_ENDPOINT=${API_ENDPOINT}cron/result
# Send the output to the API endpoint, with the API key and job ID and a boolean indicating whether the command was successful
curl -X POST -H "Content-Type: application/json" -d "{\"api_key\":\"${API_KEY}\",\"job_id\":\"${JOB_ID}\",\"error\":\"${ERROR}\",\"success\":${BOOL}}" ${API_RUNNER_ENDPOINT}
# API test curl
curl -X POST -H "Content-Type: application/json" -d "{\"api_key\":\"apikey123\",\"job_id\":\"certbot\",\"error\":\"error123\",\"success\":true}" "http://localhost:8123/api/v1/cron/result"
# If the BOOL is true, the command succeeded, so return 0, otherwise return 1
if [ "$BOOL" = "true" ]; then
    exit 0
else
    echo "Command failed" >&2
    exit 1
fi