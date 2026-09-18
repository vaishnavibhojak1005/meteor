import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';

const API_BASE = 'http://127.0.0.1:8000';

function Dashboard() {
  const [datasets, setDatasets] = useState([]);
  const [qualityData, setQualityData] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchData() {
      try {
        const datasetsResponse = await axios.get(`${API_BASE}/datasets`);
        const fetchedDatasets = datasetsResponse.data.datasets;
        setDatasets(fetchedDatasets);

        const qualityResults = {};
        for (const dataset of fetchedDatasets) {
          const qualityResponse = await axios.get(
            `${API_BASE}/datasets/${dataset.dataset_id}/quality`
          );
          qualityResults[dataset.dataset_id] = qualityResponse.data;
        }
        setQualityData(qualityResults);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, []);

  if (loading) return <p>Loading Meteor dashboard...</p>;
  if (error) return <p>Error: {error}</p>;

  return (
    <>
      <p className="subtitle">Data Observability & Quality Monitoring</p>

      <div className="dataset-grid">
        {datasets.map((dataset) => {
          const quality = qualityData[dataset.dataset_id];
          const score = quality?.quality_score?.overall_quality_score ?? '—';
          const status = quality?.quality_score?.overall_status ?? 'UNKNOWN';

          return (
            <Link
              to={`/datasets/${dataset.dataset_id}`}
              key={dataset.dataset_id}
              className={`dataset-card ${status.toLowerCase()}`}
            >
              <h2>{dataset.name}</h2>
              <p className="score">{score}%</p>
              <p className={`status-badge ${status.toLowerCase()}`}>{status}</p>
              <p className="records">{quality?.record_count ?? '—'} records</p>
            </Link>
          );
        })}
      </div>
    </>
  );
}

export default Dashboard;