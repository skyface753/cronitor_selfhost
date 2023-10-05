'use client';
import { getDataForAJob } from '@/utils/api';
import { Job } from '@/utils/types';
import { useRouter } from 'next/router';
import { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';
import { ApexOptions } from 'apexcharts';

const Chart = dynamic(() => import('react-apexcharts'), { ssr: false });

import React, { Component } from 'react';

export default function Page() {
  const router = useRouter();
  console.log(router.query.id);
  const [job, setJob] = useState<Job>();
  const [loading, setLoading] = useState(true);
  const [charData, setChartData] = useState<ApexOptions>();

  useEffect(() => {
    if (router.query.id) {
      getDataForAJob(router.query.id as string).then((data: Job) => {
        setJob(data);
        setLoading(false);
        var categories = data.results.map((result) =>
          Intl.DateTimeFormat('de-DE', {
            dateStyle: 'medium',
            timeStyle: 'medium',
          }).format(new Date(result.timestamp))
        );
        var series = data.results.map((result) => result.runtime);
        var colors = data.results.map((result) =>
          result.success ? '#008000' : result.expired ? '#FFA500' : '#ff0000'
        );
        var labels = data.results.map((result) =>
          result.success ? 'Success' : result.expired ? 'Expired' : 'Failed'
        );
        // Reverse the order of the arrays
        categories.reverse();
        series.reverse();
        colors.reverse();
        labels.reverse();

        const newChartData: ApexOptions = {
          colors: colors,
          dataLabels: {
            enabled: false,
          },
          theme: {
            mode: 'dark',
          },
          chart: {
            id: 'basic-bar',
            toolbar: {
              show: false,
            },
            background: '0',
            events: {
              click(event, chartContext, config) {
                // Reversed index
                var index = data.results.length - config.dataPointIndex - 1;
                // Add related class to the row
                var rows = document.querySelectorAll('.res-table-body tr');
                rows.forEach((row) => {
                  row.classList.remove('related');
                });
                var row = document.getElementById(`row-${index}`);
                row?.classList.add('related');

                // Scroll to the row
                row?.scrollIntoView({
                  behavior: 'smooth',
                  block: 'center',
                  inline: 'center',
                });

                // Remove class after 3 seconds
                setTimeout(() => {
                  row?.classList.remove('related');
                }, 3000);
              },
            },
          },
          xaxis: {
            categories: categories,
          },
          plotOptions: {
            bar: {
              distributed: true, // this line is mandatory
              horizontal: false,
              barHeight: '85%',
            },
          },
          legend: {
            show: false,
          },
          series: [
            {
              name: 'series-1',
              data: series,
            },
          ],

          labels: labels,
        };
        console.log(newChartData);
        setChartData(newChartData);
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
      {job?.running && (
        <h2
          style={{
            display: 'flex',
            justifyContent: 'center',
          }}
        >
          <div className='lds-ring zoom-small'>
            <div></div>
            <div></div>
            <div></div>
            <div></div>
          </div>
          Running
        </h2>
      )}
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
          {job &&
            job.results &&
            job.results.map((result, index) => (
              <tr key={result._id} id={'row-' + index}>
                <td>
                  <a id={'anchor-' + index}></a>
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
      <div className='mixed-chart'>
        {(typeof window !== 'undefined' && (
          <Chart
            options={charData}
            series={charData?.series}
            type='bar'
            width='50%'
          />
        )) || <div>Loading...</div>}
      </div>
    </div>
  );
}
