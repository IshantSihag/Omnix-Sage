import React from 'react';
import './Welcome.css';
import omnixSageLogo from './assets/omnix sage logo.jpeg'; // Import the logo


function App() {
  return (
    <div className="container">
      <header className="header">
        <img src={omnixSageLogo} alt="Omnix Sage Logo" className="header-logo" />
        <p>Your trusted Buffettology Investment Analyzer</p>
      </header>
      
      <section className="main-section">
        <div className="intro">
          <h2>Welcome to Omnix Sage</h2>
          <p>Analyze your investments using principles inspired by Warren Buffett's investing strategies.</p>
        </div>
        
        <div className="features">
          <div className="feature-card">
            <h3>Investment Analysis</h3>
            <p>Comprehensive analysis based on Buffett's value investing principles.</p>
          </div>
          <div className="feature-card">
            <h3>Portfolio Management</h3>
            <p>Track and manage your portfolio efficiently with real-time updates.</p>
          </div>
          <div className="feature-card">
            <h3>Market Insights</h3>
            <p>Stay informed with the latest market trends and insights.</p>
          </div>
        </div>
      </section>
      
      <footer className="footer">
        <p>&copy; 2024 Omnix Sage. All rights reserved.</p>
      </footer>
    </div>
  );
}

export default App;
