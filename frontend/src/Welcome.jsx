import React from 'react';
import omnixSageLogo from './assets/omnix sage logo.jpeg'; // Import the logo
import { Link } from 'react-router-dom'; // Import the Link component
import './Welcome.css'; // Import the CSS file

const App = () => {
  return (
    <div className="container">
      <header className="header">
        <div className="logo-container">
          <img src={omnixSageLogo} alt="Omnix Sage Logo" className="logo-image" />
          <h1 className="site-title">Omnix Sage</h1>
        </div>
        <nav className="navbar">
          <a href="#portfolio" className="nav-item">Portfolio</a>
          <Link to="/analyser" className="nav-item">Analyser</Link>
          <a href="#positions" className="nav-item">Positions</a>
          <a href="#lookthrough" className="nav-item">Lookthrough</a>
          <a href="#about-us" className="nav-item">About Us</a>
        </nav>
      </header>
      <main className="main">
        <section className="hero-section">
          <h2 className="title">Investment Wisdom from the Greats</h2>
          <QuoteList />
        </section>
      </main>
      <footer className="footer">
        <p className="footer-text">
          &copy; {new Date().getFullYear()} Omnix Sage | Inspired by the Wisdom of Warren Buffett, Charlie Munger, and more.
        </p>
      </footer>
    </div>
  );
}

// Array of Quotes
const quotes = [
  {
    text: "The stock market is filled with individuals who know the price of everything, but the value of nothing.",
    author: "Philip Fisher"
  },
  {
    text: "It's not supposed to be easy. Anyone who finds it easy is stupid.",
    author: "Charlie Munger"
  },
  {
    text: "You can't predict. You can prepare.",
    author: "Howard Marks"
  },
  {
    text: "Rule No. 1: Never lose money. Rule No. 2: Never forget rule No. 1.",
    author: "Warren Buffett"
  },
  {
    text: "Investing is simple, but not easy.",
    author: "Warren Buffett"
  },
  {
    text: "The big money is not in the buying and selling, but in the waiting.",
    author: "Charlie Munger"
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
