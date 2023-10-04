'use client';
import { getDataForAJob } from '@/utils/api';
import { JobResult } from '@/utils/types';
import { useRouter } from 'next/router';
import { useState, useEffect } from 'react';

export default function Page() {
  const router = useRouter();
  console.log(router.query.id);
  const [jobResults, setJobResults] = useState<JobResult[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (router.query.id) {
      getDataForAJob(router.query.id as string).then((data) => {
        setJobResults(data as JobResult[]);
        setLoading(false);
      });
    }
  }, [router.query.id]);

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <div>
      <h1
        style={{
          textAlign: 'center',
          fontSize: '50px',
          color: 'white',
          backgroundColor: 'black',
          padding: '20px',
          borderRadius: '10px',
          margin: '20px',
        }}
      >
        {router.query.id}
      </h1>
      <table className='res-table'>
        <thead className='res-table-head'>
          <tr>
            <th>Timestamp</th>
            <th>Status</th>
            <th>Runtime (s)</th>
            <th>Command</th>
            <th>Content</th>
          </tr>
        </thead>
        <tbody className='res-table-body'>
          {jobResults.length > 0 &&
            jobResults.map((result) => (
              <tr key={result.timestamp}>
                <td>
                  {Intl.DateTimeFormat('de-DE', {
                    dateStyle: 'medium',
                    timeStyle: 'medium',
                  }).format(new Date(result.timestamp))}
                </td>
                <td>
                  <div className='job-status'>
                    <span
                      className={`dot tooltip ${
                        result.success
                          ? 'green'
                          : result.expired
                          ? 'orange'
                          : 'red'
                      }`}
                    ></span>{' '}
                    <span className='status-text'>
                      {result.success
                        ? 'Success'
                        : result.expired
                        ? 'Expired'
                        : 'Failed'}
                    </span>
                  </div>
                </td>
                <td className='runtime-cell'>{result.runtime}</td>
                <td>{result.command}</td>
                <td>{result.message}</td>
              </tr>
            ))}
        </tbody>
      </table>
    </div>
  );
}
