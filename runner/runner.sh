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

API_START_ENDPOINT=${API_ENDPOINT}jobs/start?job_id=${JOB_ID}
# job_id in query string
curl -s -X POST -H "Content-Type: application/json" -H "api-key: ${API_KEY}" ${API_START_ENDPOINT} > /dev/null

BOOL="true"
start=`date +%s`
if output=$(eval $C 2>&1); then
    echo "Command succeeded"
    BOOL="true"
else
    echo "Command failed"
    BOOL="false"
fi
end=`date +%s`
rumtime=$((end-start))
echo "Command took $rumtime seconds"

# Remove all newlines from the output
ERROR=$(echo "${output}" | tr -d '\n')
# Remove quotes
ERROR=$(echo "${ERROR}" | tr -d '"')
# Remove backslashes
ERROR=$(echo "${ERROR}" | tr -d '\\')
# Remove single quotes
ERROR=$(echo "${ERROR}" | tr -d "'")
# Remove } characters
ERROR=$(echo "${ERROR}" | tr -d '}')
# Remove { characters
ERROR=$(echo "${ERROR}" | tr -d '{')
# Remove [ characters
ERROR=$(echo "${ERROR}" | tr -d '[')
# Remove ] characters
ERROR=$(echo "${ERROR}" | tr -d ']')
# Remove carriage returns
ERROR=$(echo "${ERROR}" | tr -d '\r')

COMMAND=$(echo "${C}" | tr -d '\n')
COMMAND=$(echo "${COMMAND}" | tr -d '"')
COMMAND=$(echo "${COMMAND}" | tr -d '\\')
# Remove single quotes
COMMAND=$(echo "${COMMAND}" | tr -d "'")

# sleep 5
# If command took less then 5 seconds, sleep for the remainder of the 5 seconds
if [ $rumtime -lt 5 ]; then
    sleep $((5-rumtime))
fi

echo $ERROR
API_RUNNER_ENDPOINT=${API_ENDPOINT}jobs/insert
# Send the output to the API endpoint, with the API key and job ID and a boolean indicating whether the command was successful
curl -X POST -H "Content-Type: application/json" -d "{\"job_id\":\"${JOB_ID}\",\"output\":\"${ERROR}\",\"is_success\":${BOOL},\"command\":\"${COMMAND}\",\"runtime\":${rumtime},\"started_at\":${start},\"finished_at\":${end}}" -H "api-key: ${API_KEY}" ${API_RUNNER_ENDPOINT}
# If the BOOL is true, the command succeeded, so return 0, otherwise return 1
if [ "$BOOL" = "true" ]; then
    exit 0
else
    echo "Command failed" >&2
    exit 1
fi
