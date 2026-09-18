import { useEffect, useState } from 'react';
import axios from 'axios';

const API_BASE = 'http://127.0.0.1:8000';

function Incidents() {
  const [incidents, setIncidents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchIncidents() {
      try {
        const response = await axios.get(`${API_BASE}/incidents`);
        setIncidents(response.data.incidents);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    fetchIncidents();
  }, []);

  if (loading) return <p>Loading incidents...</p>;
  if (error) return <p>Error: {error}</p>;

  return (
    <div className="incidents-page">
      <h2>Incidents</h2>
      {incidents.length === 0 ? (
        <p>No incidents recorded.</p>
      ) : (
        <table className="incidents-table">
          <thead>
            <tr>
              <th>Incident ID</th>
              <th>Type</th>
              <th>Severity</th>
              <th>Deviation</th>
              <th>Root Cause</th>
              <th>Status</th>
              <th>Created</th>
            </tr>
          </thead>
          <tbody>
            {incidents.map((incident) => (
              <tr key={incident.incident_id}>
                <td>{incident.incident_id}</td>
                <td>{incident.incident_type}</td>
                <td>
                  <span className={`severity-badge ${incident.severity.toLowerCase()}`}>
                    {incident.severity}
                  </span>
                </td>
                <td>{incident.deviation}%</td>
                <td>{incident.root_cause}</td>
                <td>
                  <span className={`status-badge-sm ${incident.status.toLowerCase()}`}>
                    {incident.status}
                  </span>
                </td>
                <td>{new Date(incident.created_at).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default Incidents;