import axios from 'axios';
import { API_URL } from './constants';
import { Job, JobResult } from './types';

export async function getCrons() {
  const { data } = await axios.get(API_URL + '/jobs/');
  const jobs: Job[] = data as Job[];
  // Reverse the runsResults array so that the most recent run is first
  for (let i = 0; i < jobs.length; i++) {
    jobs[i].runsResults.reverse();
  }
  return jobs;
}

export async function getDataForAJob(id: string): Promise<Job> {
  let { data } = await axios.get(API_URL + '/jobs/' + id);
  const job: Job = data.job;
  return job;
}
