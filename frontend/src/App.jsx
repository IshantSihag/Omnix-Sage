import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import Welcome from './Welcome';
import Home from './Home';
import omnixSageLogo from './assets/omnix sage logo.jpeg'; // Import the logo
import './App.css';

function App() {

  return (
    <Router>
      <nav>
        {/* <Link to="/">
          <img src={omnixSageLogo} alt="Omnix Sage Logo" className="navbar-logo" />
        </Link> */}
      </nav>
      <Routes>
        <Route path="/" element={<Welcome />} />
        <Route path="/home" element={<Home />} />
      </Routes>
    </Router>
  );
}

export default App;