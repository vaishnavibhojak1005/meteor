import { Routes, Route, Link } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import DatasetDetail from './pages/DatasetDetail';
import './App.css';

function App() {
  return (
    <div className="container">
      <Link to="/" className="app-title-link">
        <h1>☄️ Meteor Dashboard</h1>
      </Link>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/datasets/:id" element={<DatasetDetail />} />
      </Routes>
    </div>
  );
}

export default App;