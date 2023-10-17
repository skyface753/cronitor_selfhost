export type Job = {
  id: string;
  cron: string;
  grace_time: number;
  is_waiting: boolean;
  is_running: boolean;
  has_failed: boolean;
  has_expired: boolean;
  runsResults: JobResult[];
};
export type JobResult = {
  id: number;
  job: null;
  job_id: string;
  started_at: string;
  finished_at: string;
  result: JobRunResult;
  // is_success: boolean;
  // error: string; // failed, expired
  command: string;
  output: string;
  runtime: number;
};

export type JobRunResult = 'SUCCESS' | 'FAILED' | 'EXPIRED';
