import React from 'react';
export const SkyLoader = () => {
  return (
    <div className='cloud-container'>
      <svg
        xmlns='http://www.w3.org/2000/svg'
        viewBox='7.87722 9.61948 33.01 16.88'
      >
        <path
          d='M 12 26 H 37 C 42 26 41 20 37 20 C 38 18 37 15 33 16 C 32 8 15 8 14 17 C 8 16 6 25 12 26'
          className='cloud-back'
        />
        <path
          d='M 12 26 H 37 C 42 26 41 20 37 20 C 38 18 37 15 33 16 C 32 8 15 8 14 17 C 8 16 6 25 12 26'
          className='cloud-front'
        />
      </svg>
    </div>
  );
};
