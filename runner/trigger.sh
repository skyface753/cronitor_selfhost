MYDIR="$(dirname "$(realpath "$0")")"
source "$MYDIR/config.sh"


JOB_ID=$1
GRACE_TIME=$2 # In seconds

# API_TRIGGER_ENDPOINT=${API_ENDPOINT}cron/trigger
# In docker compose network
API_TRIGGER_ENDPOINT=http://server:8080/api/v1/cron/trigger
curl -X POST -H "Content-Type: application/json" -sS -d "{\"api_key\":\"${API_KEY}\",\"job_id\":\"${JOB_ID}\",\"grace_time\":${GRACE_TIME}}" ${API_TRIGGER_ENDPOINT}


echo "Triggered job ${JOB_ID}"