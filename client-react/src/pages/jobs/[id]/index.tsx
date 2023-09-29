'use client';
import { getDataForAJob } from '@/utils/api';
import { API_URL } from '@/utils/constants';
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
      {/* <ul>
        {jobResults.length > 0 &&
          jobResults.map((result) => (
            <li key={result.timestamp}>
              {Intl.DateTimeFormat('de-DE', {
                dateStyle: 'medium',
                timeStyle: 'medium',
              }).format(new Date(result.timestamp))}
              <br />
              {'Success: '}
              {result.success.toString()}
              <br />
              {result.content}
            </li>
          ))}
      </ul> */}
      <table className='res-table'>
        <thead className='res-table-head'>
          <tr>
            <th>Timestamp</th>
            <th>Success</th>
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
                <td>{result.success.toString()}</td>
                <td>{result.command}</td>
                <td>{result.message}</td>
              </tr>
            ))}
        </tbody>
      </table>
    </div>
  );
}
