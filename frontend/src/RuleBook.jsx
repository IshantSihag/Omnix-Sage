import React, { useState } from 'react';
import { Link } from 'react-router-dom'; // Import Link from react-router-dom
import './RuleBook.css'; // Import CSS for styling
import { Header, Footer } from './header'; // Import the Header and Footer components
import paragraphtext from './rulebook_content';

function RuleBook() {
  return (
    <div>
    <Header />
      <pre style={{backgroundcolor:'#f5f5dc',padding: 20,}}>{paragraphtext}</pre>
    <Footer />
    </div>
  );
}

export default RuleBook;