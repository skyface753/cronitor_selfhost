import axios from 'axios';
import { API_URL } from './constants';
import { Job, JobResult } from './types';

export async function getCrons() {
  const { data } = await axios.get(API_URL + '/jobs/');
  // [
  //   {
  //     "job_id": "certbot",
  //     "results": [
  //       {
  //         "_id": "651579324b345af02162f021",
  //         "job_id": "certbot",
  //         "success": false,
  //         "message": "Neuester Eintrag",
  //         "timestamp": "2021-01-01T00:00:00.000Z"
  //       },
  //       {
  //         "_id": "651579324b345af02162f020",
  //         "job_id": "certbot",
  //         "success": true,
  //         "message": "Test Message",
  //         "timestamp": "2021-01-01T00:00:00.000Z"
  //       },
  //     },
  //     {}
  //   ]
  const jobs: Job[] = [];
  for (let i = 0; i < Object.keys(data).length; i++) {
    const job: Job = {
      job_id: data[i].job_id,
      results: data[i].results.reverse(),
    };

    jobs.push(job);
  }

  return jobs;
}

export async function getDataForAJob(id: string): Promise<JobResult[]> {
  const { data } = await axios.get(API_URL + '/jobs/' + id);
  const results: JobResult[] = [];
  for (let i = 0; i < Object.keys(data).length; i++) {
    const result: JobResult = {
      _id: data[i]._id,
      job_id: data[i].job_id,
      success: data[i].success,
      message: data[i].message,
      command: data[i].command,
      timestamp: data[i].timestamp,
    };
    results.push(result);
  }
  return results;
}
