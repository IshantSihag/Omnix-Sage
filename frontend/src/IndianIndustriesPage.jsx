import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import ClipLoader from 'react-spinners/ClipLoader';
import './IndianIndustriesPage.css';

const IndianIndustriesPage = () => {
  const { key } = useParams();
  const [data, setData] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(`http://localhost:8000/api/indianIndustry?r=${key}`);
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        const result = await response.text(); // Assuming the API returns a string
        console.log("Result ", result);
        setData(result);
      } catch (error) {
        console.error('Error fetching data:', error);
        setError(error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [key]);

  return (
    <div>
      <h1>Indian Economy Data for {key}</h1>
      {loading ? (
        <ClipLoader size={50} color={"#123abc"} loading={loading} />
      ) : error ? (
        <div>Error: {error.message}</div>
      ) : (
        <div className='economy-wrapper'>
          <p dangerouslySetInnerHTML={{ __html: data.replace(/^"|"$/g, '<br>') }}></p>
        </div>
      )}
    </div>
  );
};

export default IndianIndustriesPage;