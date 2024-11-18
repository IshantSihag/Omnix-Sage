import React, { useState } from 'react';
import './Welcome.css'; // Import the CSS file
import { Header, Footer } from './header'; // Import the Header component

const App = () => {
  const [showDisclaimer, setShowDisclaimer] = useState(true);

  const handleAgree = () => {
    setShowDisclaimer(false);
  };

  const handleDisagree = () => {
    document.body.innerHTML = '';
  };

  return (
    <div>
      {showDisclaimer && (
        <div className="overlay">
          <DisclaimerPopup onAgree={handleAgree} onDisagree={handleDisagree} />
        </div>
      )}
      <div className={`container ${showDisclaimer ? 'blur' : ''}`}>
        <Header />
        <main className="main">
          <section className="hero-section">
            <h2 className="title">Investment Wisdom from the Greats</h2>
            <QuoteList />
          </section>
        </main>
        <Footer />
      </div>
    </div>
  );
};

// DisclaimerPopup Component
const DisclaimerPopup = ({ onAgree, onDisagree }) => (
  <div className="disclaimer-popup">
    <h2>Disclaimer - NO INVESTMENT ADVICE PROVIDED</h2>
    <p>This software is designed for informational purposes only and is not intended to provide personalized investment advice. The information and data provided through this software are for general guidance and educational purposes.</p>
    <p>While reasonable endeavors have been made to present reliable data in the report / presentation, but Omnix Sage
does not guarantee the accuracy or completeness of the data in the report / presentation. Omnix Sage or any of
its connected persons including its subsidiaries or associates or partners or employees shall not be in any way responsible for any loss or
damage that may arise to any person from any inadvertent error in the information contained, views and opinions expressed in this
report / presentation. Past performance should not be taken as an indication or guarantee of future performance, and no rereport / presentation or
warranty, express or implied, is made regarding future performance. Information, opinions and estimates contained in this report / presentation
reflect a judgment of its original date of publication by Omnix Sage and are subject to change without
notice. This report / presentation is not directed or intended for distribution to, or use by, any person or entity who is a citizen or resident of or
located in any locality, state, country or other jurisdiction, where such distribution, publication, availability or use would be contrary to local
law, regulation or which would subject Omnix Sage and its affiliates to any registration or licensing
requirement within such jurisdiction The product described herein may or may not be eligible for sale in all jurisdictions or to certain
category of investors. Persons in whose possession this report / presentation may come are required to inform themselves of and to observe
such restrictions. Before making any investments, the readers are advised to seek independent professional advice, verify the contents in
order to arrive at an informed investment decision.</p>
    <button className="home-button" onClick={onAgree}>Agree</button>
    <button className="home-button" onClick={onDisagree}>Disagree</button>
  </div>
);

// Array of Quotes
const quotes = [
  {
    text: "It seems logical that even before thinking of buying any common stock, the first step is to see how money has been most successfully made in the past.",
    author: "Philip Fisher"
  },
  {
    text: "Investing is simple, but not easy.",
    author: "Warren Buffett"
  },
  {
    text: "Rule No. 1: Never lose money. Rule No. 2: Never forget rule No. 1.",
    author: "Warren Buffett"
  },
  {
    text: "Risk comes from not knowing what you're doing.",
    author: "Warren Buffett"
  }
];

// Component to Render Quotes
const QuoteList = () => (
  <div className="quote-section">
    {quotes.map((quote, index) => (
      <p key={index} className={`quote ${index % 2 === 0 ? 'align-right' : 'align-left'}`}>
        "{quote.text}" 
        <span className="author">— {quote.author}</span>
      </p>
    ))}
  </div>
);

export default App;