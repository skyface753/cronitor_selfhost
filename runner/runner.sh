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

ERROR=$(eval $C 2>&1 >/dev/null)

# OUTPUT=$(eval $C)
# echo "${OUTPUT}"

BOOL="true"
# If ERROR is not empty, the command failed, so set the boolean to false
if [ -n "${ERROR}" ]; then
    BOOL="false"
fi
# Remove all newlines from the output
ERROR=$(echo "${ERROR}" | tr -d '\n')
sleep 5
API_RUNNER_ENDPOINT=${API_ENDPOINT}cron/result
# Send the output to the API endpoint, with the API key and job ID and a boolean indicating whether the command was successful
curl -X POST -H "Content-Type: application/json" -d "{\"api_key\":\"${API_KEY}\",\"job_id\":\"${JOB_ID}\",\"error\":\"${ERROR}\",\"success\":${BOOL}}" ${API_RUNNER_ENDPOINT}
