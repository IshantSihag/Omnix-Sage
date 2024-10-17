import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Header, Footer } from './header';
import './IndianEconomy.css';

function IndianEconomy() {
  let data = {
    'Domestic Investments': 'economy/domestic-investments',
    'Economic Survey 2023-24': 'economy/economic-survey-2023-24',
    'Foreign Direct Investment': 'economy/foreign-direct-investment',
    'Foreign Institutional Investors': 'economy/foreign-institutional-investors',
    'Foreign Trade Policy 2023': 'economy/foreign-trade-policy-2023',
    'Government Schemes': 'economy/government-schemes',
    'India Positive': 'economy/india-positive',
    'India: A Snapshot': 'economy/indiasnapshot/about-india-at-a-glance',
    'Indian Economy News': 'indian-economy-news',
    'Indian Economy Overview': 'economy/indian-economy-overview',
    'Indian Investments Abroad': 'economy/indian-investments-abroad',
    'Investments': 'economy/investments',
    'Make in India': 'economy/make-in-india',
    'Monthly Economic Report': 'economy/monthly-economic-report',
    'Policy Watch': 'news/policy-watch',
    'Quick Facts': 'economy/indiasnapshot/facts-about-indian-economy',
    'Startup India': 'economy/startup-india',
    'Trade': 'economy/trade-and-external-sector',
    'Union Budget 2024-25': 'economy/union-budget-2024-25',
    'Useful Links': 'economy/directory/india-directory'
  };
  return (
    <div className='indian-economy-container'>
      <Header />
      <div className="content">
        {Object.keys(data).map(key => (
          <Link to={`/indian-economy/${encodeURIComponent(data[key])}`} key={key} rel="noopener noreferrer">
            <button>{key}</button>
          </Link>
        ))}
      </div>
      <Footer />
    </div>
  );
}

export default IndianEconomy;