import React, { useState } from 'react';
import { Link } from 'react-router-dom'; // Import Link from react-router-dom
import './RuleBook.css'; // Import CSS for styling
import { Header, Footer } from './header'; // Import the Header and Footer components

function RuleBook() {
  return (
    <div>
    <Header />
      <p>Here are the rules to follow when investing in the stock market:</p>
      <ul>
        <li>Invest for long term</li>
            <ul>Buy businesses ypou believe can grow steadily over 10+ years</ul>
        <li>Focus on Quality Businesses</li>
            <ul>Businesses with High ROE , Strong Cash Flow and consistent Earinngs with low debt</ul>
        <li>Buy at a reasonable price</li>
            <ul>Buy when the stock is trading at P/E less than PAT CAGR</ul>
        <li>Be contrarian and think independently </li>
            <ul>Based your decision on sound analysis</ul>
        <li>Understand what you invest in</li>
            <ul>Learn how they operate , generate profit and grow</ul>
        <li>Risk management is key</li>
            <ul>Consider potential risk and ensure they are managable</ul>
        <li>Keep it simple</li>
            <ul>Avoid speculation</ul>
        
          
      </ul>
    <Footer />
    </div>
  );
}

export default RuleBook;