import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import Welcome from './Welcome';
import Home from './Home';
import Analyser from './Analyser'; // Import the Analyser component
import RuleBook from './RuleBook'; // Import the RuleBook component
import Report from './Report'; // Import the Report component
import IndianEconomy from './IndianEconomy'; // Import the IndianEconomy component
import IndianEconomyPage from './IndianEconomyPage'; // Adjust the path as necessary
import IndianIndustries from './IndianIndustries'; // Import the IndianIndustries component
import IndianIndustriesPage from './IndianIndustriesPage'; // Adjust the path as necessary
import './App.css';


function App() {
  return (
    <Router>
      
      <Routes>
        <Route path="/" element={<Welcome />} />
        <Route path="/home" element={<Home />} />
        <Route path="/analyser" element={<Analyser />} /> {/* Add route for Analyser */}
        <Route path="/rulebook" element={<RuleBook />} /> {/* Add route for Analyser */}
        <Route path="/indian-economy" element={<IndianEconomy />} /> {/* Add route for Analyser */}
        <Route path="/indian-industries" element={<IndianIndustries />} /> {/* Add route for Analyser */}
        <Route path="/indian-industries/:key" element={<IndianIndustriesPage />} /> {/* Add route for IndianEconomyPage */}
        <Route path="/indian-economy/:key" element={<IndianEconomyPage />} /> {/* Add route for IndianEconomyPage */}
        <Route path="/report" element={<Report />} /> {/* Add route for Report */}
      </Routes>
    </Router>
  );
}

export default App;