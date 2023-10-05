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
                  <div className='card-header'>
                    {job.running && (
                      <div className='lds-ring zoom-small'>
                        <div></div>
                        <div></div>
                        <div></div>
                        <div></div>
                      </div>
                    )}
                    <h1>{job.job_id}</h1>
                  </div>
                  {job.results.length > 0 && (
                    <p>
                      {Intl.DateTimeFormat('de-DE', {
                        dateStyle: 'medium',
                        timeStyle: 'medium',
                      }).format(
                        new Date(job.results[job.results.length - 1].timestamp)
                      )}
                      <br />
                      {job.results[job.results.length - 1].success
                        ? 'Success'
                        : job.results[job.results.length - 1].expired
                        ? 'Expired'
                        : 'Failed'}
                      <br />
                      {'Runtime: '}
                      {job.results[job.results.length - 1].runtime} seconds
                    </p>
                  )}
                </a>

                <ul className='hlist'>
                  {job.results.map((result) => (
                    <li key={result._id}>
                      <span
                        className={`dot tooltip ${
                          result.success
                            ? 'green'
                            : result.expired
                            ? 'orange'
                            : 'red'
                        }`}
                      >
                        <span className='tooltiptext'>
                          {Intl.DateTimeFormat('de-DE', {
                            dateStyle: 'medium',
                            timeStyle: 'medium',
                          }).format(new Date(result.timestamp))}{' '}
                          <br />
                          {result.success
                            ? 'Success'
                            : result.expired
                            ? 'Expired'
                            : 'Failed'}
                        </span>
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
