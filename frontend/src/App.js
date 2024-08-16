import React from 'react';
import { BrowserRouter as Router, Route, Link, Routes } from 'react-router-dom';
import SearchFood from './Components/Pages/SearchFood';
import LogFood from './Components/Pages/LogFood'; // Import the LogFood component
import AnalyzeActivity from './Components/Pages/AnalyzeActivity';

function App() {
  return (
    <Router>
      <div className="max-w-6xl mx-auto px-4">
        <nav className="bg-gray-800 text-white p-4 rounded-md">
          <ul className="flex space-x-4">
            <li>
              <Link to="/search-food" className="hover:bg-gray-700 p-2 rounded">Search Food</Link>
            </li>
            <li>
              <Link to="/log-food" className="hover:bg-gray-700 p-2 rounded">Log Food</Link>
            </li>
            <li>
              <Link to="/analyze-activity" className="hover:bg-gray-700 p-2 rounded">Analyze Activity</Link>
            </li>
          </ul>
        </nav>

        <Routes>
          <Route path="/search-food" element={<SearchFood />} />
          <Route path="/log-food" element={<LogFood />} />
          <Route path="/analyze-activity" element={<AnalyzeActivity />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;