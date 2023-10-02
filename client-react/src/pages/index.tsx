import { useEffect, useState } from 'react';
import { SkyLoader } from '@/components/loader/skyloader';
import { Job } from '@/utils/types';
import { getCrons } from '@/utils/api';

export default function Home() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(false);

  async function loadCrons() {
    setJobs(await getCrons());
    setLoading(false);
  }

  useEffect(() => {
    setLoading(true);
    loadCrons();
  }, []);

  if (loading) {
    return <SkyLoader />;
  }

  console.log(jobs);

  return (
    <main>
      <div>
        <div className='row'>
          {jobs.map((job) => (
            <div className='column' key={job.job_id}>
              <div className='card'>
                <a href={`/jobs/${job.job_id}`}>
                  <h1>{job.job_id}</h1>
                  {job.results.length > 0 && (
                    <p>
                      {Intl.DateTimeFormat('de-DE', {
                        dateStyle: 'medium',
                        timeStyle: 'medium',
                      }).format(
                        new Date(job.results[job.results.length - 1].timestamp)
                      )}
                      <br />
                      {'Success: '}
                      {job.results[job.results.length - 1].success.toString()}
                    </p>
                  )}
                </a>

                <ul className='hlist'>
                  {job.results.map((result) => (
                    <li key={result.timestamp}>
                      <span
                        className={`dot tooltip ${
                          result.success
                            ? 'green'
                            : result.expired
                            ? 'orange'
                            : 'red'
                        }`}
                      >
                        <span className='tooltiptext'>{result.timestamp}</span>
                      </span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          ))}
        </div>
      </div>
    </main>
  );
}
