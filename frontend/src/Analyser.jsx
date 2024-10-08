import React, { useState } from 'react';
import { Link } from 'react-router-dom'; // Import Link from react-router-dom
import './Analyser.css'; // Import CSS for styling
import { Header, Footer } from './header'; // Import the Header and Footer components

function Analyser() {
  const [query, setQuery] = useState('');
  const [suggestions, setSuggestions] = useState([]);

  const handleInputChange = async (event) => {
    const value = event.target.value;
    setQuery(value);

    if (value.length > 0) {
      try {
        const response = await fetch(`http://localhost:8000/api/search?company=${value}`);
        const data = await response.json();
        setSuggestions(data); // Update the suggestions state with the API response
      } catch (error) {
        console.error('Error fetching suggestions:', error);
        setSuggestions([]);
      }
    } else {
      setSuggestions([]);
    }
  };

  return (
    <div className="analyser-container">
      <Header />
      <div className="search-bar-container">
        <input
          type="text"
          value={query}
          onChange={handleInputChange}
          placeholder="Search for a company..."
          className="search-bar"
        />
        <ul className="suggestions-list">
          {suggestions.map((suggestion) => (
            <li key={suggestion.id}>
              <Link
                to="/report"
                state={{ company: suggestion }}
                className="suggestion-link"
              >
                {suggestion.name}
              </Link>
            </li>
          ))}
        </ul>
      </div>
      <Footer />
    </div>
  );
}

export default Analyser;