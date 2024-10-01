import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import Welcome from './Welcome';
import Home from './Home';
import Analyser from './Analyser'; // Import the Analyser component
import RuleBook from './RuleBook'; // Import the RuleBook component
import Report from './Report'; // Import the Report component
import omnixSageLogo from './assets/omnix sage logo.jpeg'; // Import the logo
import './App.css';

function App() {
  return (
    <Router>
      
      <Routes>
        <Route path="/" element={<Welcome />} />
        <Route path="/home" element={<Home />} />
        <Route path="/analyser" element={<Analyser />} /> {/* Add route for Analyser */}
        <Route path="/rulebook" element={<RuleBook />} /> {/* Add route for Analyser */}
        <Route path="/report" element={<Report />} /> {/* Add route for Report */}
      </Routes>
    </Router>
  );
}

export default App;