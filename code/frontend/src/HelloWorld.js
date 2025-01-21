import React, { useEffect, useState } from 'react';

const HelloWorld = () => {
  const [message, setMessage] = useState('');

  useEffect(() => {
    // Verzoek naar de Flask API
    fetch('http://localhost:5000/api/hello')
      .then((response) => response.json())
      .then((data) => {
        setMessage(data.message); // Sla het bericht op in de state
      })
      .catch((error) => console.error('Error fetching data:', error));
  }, []);

  return (
    <div>
      <h1>{message ? message : 'Loading...'}</h1>
    </div>
  );
};

export default HelloWorld;
