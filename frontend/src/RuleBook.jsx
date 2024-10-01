import React, { useState } from 'react';
import { Link } from 'react-router-dom'; // Import Link from react-router-dom
import './RuleBook.css'; // Import CSS for styling
import { Header, Footer } from './header'; // Import the Header and Footer components

function RuleBook() {
  return (
    <div>
    <Header />
      <h1>Rule Book</h1>
      <p>Here are the rules to follow when investing in the stock market:</p>
      <ul>
        <li>Rule 1: Don't lose money.</li>
        <li>Rule 2: Don't forget Rule 1.</li>
      </ul>
    <Footer />
    </div>
  );
}

export default RuleBook;