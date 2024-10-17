import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Header, Footer } from './header';
import './IndianIndustries.css';

function IndianIndustries() {
  let data = {   
    'Agriculture and Allied Industries': 'agriculture-india',
    'Auto Components': 'autocomponents-india',
    'Automobiles': 'india-automobiles',
    'Aviation': 'indian-aviation',
    'Ayush': 'ayush',
    'Banking': 'banking-india',
    'Biotechnology': 'biotechnology-india',
    'Cement': 'cement-india',
    'Chemicals': 'chemical-industry-india',
    'Consumer Durables': 'indian-consumer-market',
    'Defence Manufacturing': 'defence-manufacturing',
    'E-Commerce': 'ecommerce',
    'Education and Training': 'education-sector-india',
    'Electric Vehicle': 'electric-vehicle',
    'Electronics System Design & Manufacturing': 'electronics-system-design-manufacturing-esdm',
    'Engineering and Capital Goods': 'engineering-india',
    'Financial Services': 'financial-services-india',
    'FMCG': 'fmcg',
    'Food Processing': 'food-processing',
    'Gems and Jewellery': 'gems-jewellery-india',
    'Healthcare': 'healthcare-india',
    'Infrastructure': 'infrastructure-sector-india',
    'Insurance': 'insurance-sector-india',
    'IT & BPM': 'information-technology-india',
    'Manufacturing': 'manufacturing-sector-india',
    'Media and Entertainment': 'media-entertainment-india',
    'Medical Devices': 'medical-devices',
    'Metals and Mining': 'metals-and-mining',
    'MSME': 'msme',
    'Oil and Gas': 'oil-gas-india',
    'Paper & Packaging': 'paper-packaging',
    'Pharmaceuticals': 'pharmaceutical-india',
    'Ports': 'ports-india-shipping',
    'Power': 'power-sector-india',
    'Railways': 'indian-railways',
    'Real Estate': 'real-estate-india',
    'Renewable Energy': 'renewable-energy',
    'Retail': 'retail-india',
    'Roads': 'roads-india',
    'Science and Technology': 'science-and-technology',
    'Services': 'services',
    'Steel': 'steel',
    'Telecommunications': 'telecommunications',
    'Textiles': 'textiles',
    'Tourism and Hospitality': 'tourism-hospitality-india',
  };
  return (
    <div className='indian-industries-container'>
      <Header />
      <div className="content">
        {Object.keys(data).map(key => (
          <Link to={`/indian-industries/${encodeURIComponent(data[key])}`} key={key} rel="noopener noreferrer">
            <button>{key}</button>
          </Link>
        ))}
      </div>
      <Footer />
    </div>
  );
}

export default IndianIndustries;