#!/bin/bash

MYDIR="$(dirname "$(realpath "$0")")"
source "$MYDIR/config.sh"


API_LIST_DISABLED_JOBS_ENDPOINT=${API_ENDPOINT}jobs/?show_disabled=true
# curl -X 'GET' ${API_LIST_DISABLED_JOBS_ENDPOINT} -H 'accept: application/json'
JOBS=$(curl -s -X 'GET' ${API_LIST_DISABLED_JOBS_ENDPOINT} -H 'accept: application/json' -H "api-key: ${API_KEY}")
echo "Disabled jobs:"
echo 
echo "${JOBS}" | jq -r '.[] | "\(.id)"'
echo 
# Wait for input
read -p "Enter job id to delete: " JOB_ID



API_DELETE_ENDPOINT=${API_ENDPOINT}jobs/${JOB_ID}
# job_id in query string
curl -s -X DELETE -H "Content-Type: application/json" -H "api-key: ${API_KEY}" ${API_DELETE_ENDPOINT} 
