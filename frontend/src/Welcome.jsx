import React from 'react';
import './Welcome.css'; // Import the CSS file
import {Header, Footer} from './header'; // Import the Header component

const App = () => {
  return (
    <div className="container">
      <Header />
      <main className="main">
        <section className="hero-section">
          <h2 className="title">Investment Wisdom from the Greats</h2>
          <QuoteList />
        </section>
      </main>
      <Footer />
    </div>
  );
}

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
