#!/bin/bash


# Load the API endpoint and API key from the source file
# TODO: Make this configurable
# source /etc/cron-runner/config.sh
source ./config.sh

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
# Run the command
OUTPUT=$(eval $C)
# echo "${OUTPUT}"

BOOL="true"
if [ $? -ne 0 ]; then
    BOOL="false"
fi

# Send the output to the API endpoint, with the API key and job ID and a boolean indicating whether the command was successful
curl -X POST -H "Content-Type: application/json" -d "{\"api_key\":\"${API_KEY}\",\"job_id\":\"${JOB_ID}\",\"output\":\"${OUTPUT}\",\"success\":${BOOL}}" ${API_ENDPOINT}
