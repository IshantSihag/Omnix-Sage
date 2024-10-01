import React from 'react';
import './Welcome.css'; // Import the CSS file
import omnixSageLogo from './assets/omnix sage logo.jpeg'; // Import the logo
import { Link } from 'react-router-dom'; // Import the Link component

const Header = () => {
    return (<header className="header">
        <div className="logo-container">
            <img src={omnixSageLogo} alt="Omnix Sage Logo" className="logo-image" />
            <h1 className="site-title">Omnix Sage</h1>
        </div>
        <nav className="navbar">
            <a href="#portfolio" className="nav-item">Core Portfolio</a>
            <Link to="/analyser" className="nav-item">Slipstream Finder</Link>
            <a href="#positions" className="nav-item">Positions</a>
            <a href="#positions" className="nav-item">Sattelite Portfolio</a>
            <Link to="/rulebook" className="nav-item">Rule Book</Link>
            <a href="#about-us" className="nav-item">About Us</a>
        </nav>
    </header>)
}

const Footer = () => {
    return (<footer className="footer">
        <p className="footer-text">
          &copy; {new Date().getFullYear()} Omnix Sage | Inspired by the Wisdom of Warren Buffett, Charlie Munger, and more.
        </p>
      </footer>)
}

export { Header, Footer }; // Export the Header component