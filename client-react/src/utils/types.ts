export type Job = {
  job_id: string;
  running: boolean;
  results: JobResult[];
};
export type JobResult = {
  _id: string;
  job_id: string;
  timestamp: string;
  success: boolean;
  expired: boolean;
  message: string;
  command: string;
  runtime: number;
};
