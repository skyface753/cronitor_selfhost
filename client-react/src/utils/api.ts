import axios from 'axios';
import { API_URL } from './constants';
import { Job, JobResult } from './types';

export async function getCrons() {
  const { data } = await axios.get(API_URL + '/cron/status');
  const jobs: Job[] = [];
  for (let i = 0; i < Object.keys(data).length; i++) {
    const jobid = Object.keys(data)[i];
    const results: JobResult[] = [];
    for (let j = 0; j < Object.keys(data[jobid]).length; j++) {
      const timestamp = Object.keys(data[jobid])[j];
      const success = data[jobid][timestamp].Success;
      const content = data[jobid][timestamp].Content;
      results.push({ timestamp, success, content });
    }
    jobs.push({ jobid, results });
  }

  return jobs;
}

export async function getDataForAJob(id: string): Promise<JobResult[]> {
  const { data } = await axios.get(API_URL + '/cron/status/job/' + id);
  const results: JobResult[] = [];
  for (let j = 0; j < Object.keys(data).length; j++) {
    const timestamp = Object.keys(data)[j];
    const success = data[timestamp].Success;
    const content = data[timestamp].Content;
    results.push({ timestamp, success, content });
  }
  results.reverse();
  return results;
}
