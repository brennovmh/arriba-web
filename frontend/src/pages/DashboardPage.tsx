import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import StatusBadge from "../components/StatusBadge";
import api from "../services/api";
import { Analysis } from "../types";

export default function DashboardPage() {
  const [analyses, setAnalyses] = useState<Analysis[]>([]);
  const [statusFilter, setStatusFilter] = useState("all");
  const [pipelineFilter, setPipelineFilter] = useState("all");
  const [search, setSearch] = useState("");

  useEffect(() => {
    api.get<Analysis[]>("/analyses").then((response) => setAnalyses(response.data));
  }, []);

  const pipelineOptions = Array.from(new Set(analyses.map((analysis) => analysis.pipeline_name))).sort();
  const filteredAnalyses = analyses.filter((analysis) => {
    const status = analysis.latest_job?.status || "draft";
    const searchable = `${analysis.name} ${analysis.sample_id} ${analysis.project_name || ""}`.toLowerCase();
    if (statusFilter !== "all" && status !== statusFilter) {
      return false;
    }
    if (pipelineFilter !== "all" && analysis.pipeline_name !== pipelineFilter) {
      return false;
    }
    if (search && !searchable.includes(search.toLowerCase())) {
      return false;
    }
    return true;
  });

  return (
    <div>
      <div className="page-header">
        <div>
          <h2>Análises</h2>
          <p className="muted">Histórico recente e status atual dos jobs.</p>
        </div>
        <Link to="/analyses/new" className="primary-link">
          Nova análise
        </Link>
      </div>
      <div className="card filter-grid">
        <label>
          Buscar
          <input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="análise, amostra ou projeto" />
        </label>
        <label>
          Status
          <select value={statusFilter} onChange={(event) => setStatusFilter(event.target.value)}>
            <option value="all">Todos</option>
            <option value="draft">Draft</option>
            <option value="pending">Pending</option>
            <option value="downloading">Downloading</option>
            <option value="running">Running</option>
            <option value="uploading_results">Uploading</option>
            <option value="completed">Completed</option>
            <option value="failed">Failed</option>
            <option value="cancelled">Cancelled</option>
          </select>
        </label>
        <label>
          Pipeline
          <select value={pipelineFilter} onChange={(event) => setPipelineFilter(event.target.value)}>
            <option value="all">Todas</option>
            {pipelineOptions.map((pipelineName) => (
              <option key={pipelineName} value={pipelineName}>
                {pipelineName}
              </option>
            ))}
          </select>
        </label>
      </div>
      <div className="table-card">
        <table>
          <thead>
            <tr>
              <th>Análise</th>
              <th>Amostra</th>
              <th>Projeto</th>
              <th>Pipeline</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {filteredAnalyses.map((analysis) => (
              <tr key={analysis.id}>
                <td>
                  <Link to={`/analyses/${analysis.id}`}>{analysis.name}</Link>
                </td>
                <td>{analysis.sample_id}</td>
                <td>{analysis.project_name || "-"}</td>
                <td>{analysis.pipeline_name}</td>
                <td>
                  <StatusBadge status={analysis.latest_job?.status || "draft"} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {filteredAnalyses.length === 0 ? <p className="muted">Nenhuma análise corresponde aos filtros atuais.</p> : null}
      </div>
    </div>
  );
}
