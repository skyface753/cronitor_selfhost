export type Job = {
  jobid: string;
  results: JobResult[];
};
export type JobResult = {
  timestamp: string;
  success: boolean;
  content: string;
};
