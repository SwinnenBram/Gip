import React from 'react';

const HomePage = () => {
  return (
    <div style={{ textAlign: 'center', padding: '20px', maxWidth: '800px', margin: 'auto' }}>
      <h1>Welcome to the Smart Parking Garage!</h1>
      <p>Find information about our pricing, opening hours, and facilities below:</p>
      
      <h2>💰 Pricing</h2>
      <table style={{ width: '100%', borderCollapse: 'collapse', marginBottom: '20px' }}>
        <tbody>
          <tr><td>Minimum charge:</td><td><strong>€5.00 (1 hour)</strong></td></tr>
          <tr><td>Up to 3 hours:</td><td><strong>€5.00 per hour</strong></td></tr>
          <tr><td>3 to 6 hours:</td><td><strong>€4.00 per hour</strong></td></tr>
          <tr><td>After 6 hours:</td><td><strong>€3.00 per hour</strong></td></tr>
          <tr><td>Maximum daily rate:</td><td><strong>€20.00</strong></td></tr>
        </tbody>
      </table>

      <h2>🕒 Opening Hours</h2>
      <p><strong>Open 24/7</strong></p>

      <h2>🔹 Facilities</h2>
      <ul style={{ listStyleType: 'none', padding: 0, marginBottom: '20px' }}>
        <li>✅ Secure parking with surveillance</li>
        <li>✅ Electric vehicle charging stations</li>
        <li>✅ Handicapped-accessible parking spots</li>
        <li>✅ Contactless payment options</li>
        <li>✅ Reservation system for stress-free parking</li>
      </ul>

      <h2>📍 Location</h2>
      <p><strong>123 Smart Street, Parking City</strong></p>

      <h2>📲 Find us on Socials</h2>
        <p>
          <a href="smartparking" target="_blank" rel="noopener noreferrer" style={{ margin: '0 10px', textDecoration: 'none' }}>
            <span role="img" aria-label="Instagram">📷</span> Instagram: SmartParking
          </a>
        </p>
        <p>
          <a href="smartparking" target="_blank" rel="noopener noreferrer" style={{ margin: '0 10px', textDecoration: 'none' }}>
            <span role="img" aria-label="Facebook">📘</span> Facebook: SmartParking
          </a>
        </p>
    </div>
  );
};

export default HomePage;
