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