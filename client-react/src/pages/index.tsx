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
            <div className='column' key={job.id}>
              <div className='card'>
                <a href={`/jobs/${job.id}`}>
                  <div className='card-header'>
                    <h1
                      style={{
                        marginRight: '3px',
                      }}
                    >
                      {job.id}
                    </h1>
                    {job.is_running && (
                      <div className='lds-ring zoom-small'>
                        <div></div>
                        <div></div>
                        <div></div>
                        <div></div>
                      </div>
                    )}
                    {!job.is_running &&
                      ((job.has_failed && <div className='dot red'></div>) || (
                        <div className='dot green'></div>
                      ))}
                  </div>
                  {job.runsResults.length > 0 && (
                    <p>
                      {Intl.DateTimeFormat('de-DE', {
                        dateStyle: 'medium',
                        timeStyle: 'medium',
                      }).format(
                        new Date(
                          job.runsResults[job.runsResults.length - 1].started_at
                        )
                      )}
                      <br />
                      {job.runsResults[job.runsResults.length - 1].is_success
                        ? 'Success'
                        : job.runsResults[job.runsResults.length - 1].error ===
                          'expired'
                        ? 'Expired'
                        : 'Failed'}
                      <br />
                      {'Runtime: '}
                      {job.runsResults[job.runsResults.length - 1].runtime}{' '}
                      seconds
                    </p>
                  )}
                </a>

                <ul className='hlist'>
                  {job.runsResults.map((result) => (
                    <li key={result.id}>
                      <span
                        className={`dot tooltip ${
                          result.is_success
                            ? 'green'
                            : result.error === 'expired'
                            ? 'orange'
                            : 'red'
                        }`}
                      >
                        <span className='tooltiptext'>
                          {Intl.DateTimeFormat('de-DE', {
                            dateStyle: 'medium',
                            timeStyle: 'medium',
                          }).format(new Date(result.started_at))}
                          {' - '}
                          {Intl.DateTimeFormat('de-DE', {
                            dateStyle: 'medium',
                            timeStyle: 'medium',
                          }).format(new Date(result.finished_at))}
                          <br />
                          {result.is_success
                            ? 'Success'
                            : result.error === 'expired'
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
