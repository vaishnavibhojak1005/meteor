import { Routes, Route, Link } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import DatasetDetail from './pages/DatasetDetail';
import Incidents from './pages/Incidents';
import './App.css';

function App() {
  return (
    <div className="container">
      <div className="header-row">
        <Link to="/" className="app-title-link">
          <h1>☄️ Meteor Dashboard</h1>
        </Link>
        <nav className="main-nav">
          <Link to="/">Dashboard</Link>
          <Link to="/incidents">Incidents</Link>
        </nav>
      </div>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/datasets/:id" element={<DatasetDetail />} />
        <Route path="/incidents" element={<Incidents />} />
      </Routes>
    </div>
  );
}

export default App;