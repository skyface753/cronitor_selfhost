#!/bin/bash

CRONS=$(crontab -l)
# Remove all commented lines
CRONS=$(echo "${CRONS}" | grep -v '^#')
# Remove all empty lines
CRONS=$(echo "${CRONS}" | grep -v '^$')
# Print the crontab
# echo "${CRONS}"

# Parse the CRONS to an array
IFS=$'\n' read -rd '' -a CRONS <<<"$CRONS"
JOB_NAMES=()
JOB_SCHEDULES=()
JOB_GRACE_PERIODS=()

# Loop through the CRONS
for CRON in "${CRONS[@]}"; do
    # echo "Cron: ${CRON}"
    # get the schedule (first 5 parts of the cron)
    SCHEDULE=$(echo "${CRON}" | awk '{print $1,$2,$3,$4,$5}')
    echo "Schedule: ${SCHEDULE}"
    # get the command (the rest of the cron)
    COMMAND=$(echo "${CRON}" | awk '{$1=$2=$3=$4=$5=""; print $0}')
    echo "Command: ${COMMAND}"
    # Name of the job from input (no spaces allowed -> is used as id)
    read -p "Enter job name (empty to skip): " JOB_NAME
    if [[ -z "${JOB_NAME}" ]]; then
        continue
    fi
    # Grace-period from input
    read -p "Enter grace-period (in seconds): " GRACE_PERIOD
    # Add the job to the array if the name is not empty
    JOB_NAMES+=("${JOB_NAME}")
    JOB_SCHEDULES+=("${SCHEDULE}")
    JOB_GRACE_PERIODS+=("${GRACE_PERIOD}")
    echo "---"
done
read -p "Enter filename to write jobs to (default: jobs.json): " FILENAME
if [[ -z "${FILENAME}" ]]; then
    FILENAME="jobs.json"
fi
# Write the jobs to jobs.json
echo "Writing jobs to ${FILENAME}"
echo "{" > ${FILENAME}
for i in "${!JOB_NAMES[@]}"; do
    echo "  \"${JOB_NAMES[$i]}\": {" >> ${FILENAME}
    echo "    \"cron\": \"${JOB_SCHEDULES[$i]}\"," >> ${FILENAME}
    echo "    \"grace_time\": ${JOB_GRACE_PERIODS[$i]}" >> ${FILENAME}
    if [[ $i -eq $((${#JOB_NAMES[@]} - 1)) ]]; then
        echo "  }" >> ${FILENAME}
    else
        echo "  }," >> ${FILENAME}
    fi
done
echo "}" >> ${FILENAME}
