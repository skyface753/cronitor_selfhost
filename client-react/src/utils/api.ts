import axios from 'axios';
import { API_URL } from './constants';
import { Job, JobResult } from './types';

export async function getCrons() {
  const { data } = await axios.get(API_URL + '/jobs/');
  const jobs: Job[] = [];
  for (let i = 0; i < Object.keys(data).length; i++) {
    const job: Job = {
      job_id: data[i].job_id,
      results: data[i].results.reverse(),
      running: data[i].running,
    };

    jobs.push(job);
  }

  return jobs;
}

export async function getDataForAJob(id: string): Promise<Job> {
  let { data } = await axios.get(API_URL + '/jobs/' + id);
  const results: JobResult[] = [];
  const jobData = data['job'];
  const job_id = jobData.job_id;
  const running = jobData.running;
  data = data['jobResults'];
  for (let i = 0; i < Object.keys(data).length; i++) {
    const result: JobResult = {
      _id: data[i]._id,
      job_id: data[i].job_id,
      success: data[i].success,
      expired: data[i].expired,
      message: data[i].message,
      command: data[i].command,
      timestamp: data[i].timestamp,
      runtime: data[i].runtime,
    };
    results.push(result);
  }
  const job: Job = {
    job_id,
    running,
    results,
  };
  return job;
}
