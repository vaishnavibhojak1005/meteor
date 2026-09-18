import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import axios from 'axios';

const API_BASE = 'http://127.0.0.1:8000';

function DatasetDetail() {
  const { id } = useParams();
  const [quality, setQuality] = useState(null);
  const [anomalies, setAnomalies] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchData() {
      try {
        const [qualityRes, anomaliesRes] = await Promise.all([
          axios.get(`${API_BASE}/datasets/${id}/quality`),
          axios.get(`${API_BASE}/datasets/${id}/anomalies`),
        ]);
        setQuality(qualityRes.data);
        setAnomalies(anomaliesRes.data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, [id]);

  if (loading) return <p>Loading dataset details...</p>;
  if (error) return <p>Error: {error}</p>;

  return (
    <div className="detail-page">
      <Link to="/" className="back-link">← Back to Dashboard</Link>
      <h2 className="detail-title">{quality.dataset}</h2>

      <div className="detail-grid">
        <div className="detail-stat">
          <span className="label">Records</span>
          <span className="value">{quality.record_count}</span>
        </div>
        <div className="detail-stat">
          <span className="label">Quality Score</span>
          <span className="value">{quality.quality_score.overall_quality_score}%</span>
        </div>
        <div className="detail-stat">
          <span className="label">Completeness</span>
          <span className="value">{quality.completeness.overall_completeness_score}%</span>
        </div>
        <div className="detail-stat">
          <span className="label">Duplicates</span>
          <span className="value">{quality.duplicates.status}</span>
        </div>
        <div className="detail-stat">
          <span className="label">Freshness</span>
          <span className="value">{quality.freshness.status}</span>
        </div>
        <div className="detail-stat">
          <span className="label">Schema</span>
          <span className="value">{quality.schema.status}</span>
        </div>
        <div className="detail-stat">
          <span className="label">Anomaly Status</span>
          <span className="value">{anomalies.status}</span>
        </div>
        <div className="detail-stat">
          <span className="label">Z-Score</span>
          <span className="value">{anomalies.z_score ?? '—'}</span>
        </div>
      </div>

      <h3>Overall Status</h3>
      <p className={`status-badge ${quality.quality_score.overall_status.toLowerCase()}`}>
        {quality.quality_score.overall_status}
      </p>
    </div>
  );
}

export default DatasetDetail;