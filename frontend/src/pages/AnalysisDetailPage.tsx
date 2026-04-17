import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import FileUpload from "../components/FileUpload";
import ResultList from "../components/ResultList";
import StatusBadge from "../components/StatusBadge";
import api from "../services/api";
import { Analysis, FileRecord, JobDetails, PipelineDefinition } from "../types";

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export default function AnalysisDetailPage() {
  const { analysisId } = useParams();
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [job, setJob] = useState<JobDetails | null>(null);
  const [pipelines, setPipelines] = useState<PipelineDefinition[]>([]);
  const [reprocessPipeline, setReprocessPipeline] = useState("");

  async function loadAnalysis() {
    const response = await api.get<Analysis>(`/analyses/${analysisId}`);
    setAnalysis(response.data);
    setReprocessPipeline((current) => current || response.data.pipeline_name);
    if (response.data.latest_job) {
      const jobResponse = await api.get<JobDetails>(`/jobs/${response.data.latest_job.id}`);
      setJob(jobResponse.data);
    } else {
      setJob(null);
    }
  }

  useEffect(() => {
    api.get<PipelineDefinition[]>("/pipelines").then((response) => setPipelines(response.data));
    loadAnalysis();
    const interval = window.setInterval(loadAnalysis, 10000);
    return () => window.clearInterval(interval);
  }, [analysisId]);

  async function submitJob() {
    await api.post(`/analyses/${analysisId}/submit`);
    await loadAnalysis();
  }

  async function cancelPendingJob() {
    if (!job) {
      return;
    }
    await api.post(`/jobs/${job.id}/cancel`);
    await loadAnalysis();
  }

  async function reprocessJob() {
    await api.post(`/analyses/${analysisId}/reprocess`, { pipeline_name: reprocessPipeline });
    await loadAnalysis();
  }

  if (!analysis) {
    return <p className="muted">Carregando análise...</p>;
  }

  const resultFiles = job?.files.filter((file) => file.category !== "input") || [];

  return (
    <div className="stack-page">
      <div className="page-header">
        <div>
          <h2>{analysis.name}</h2>
          <p className="muted">
            Amostra {analysis.sample_id} {analysis.project_name ? `• ${analysis.project_name}` : ""}
          </p>
        </div>
        <StatusBadge status={analysis.latest_job?.status || "draft"} />
      </div>

      <div className="card">
        <h3>Metadados</h3>
        <p><strong>Pipeline:</strong> {analysis.pipeline_name}</p>
        <p><strong>Observações:</strong> {analysis.notes || "-"}</p>
      </div>

      <FileUpload
        analysisId={analysis.id}
        onUploaded={async (_files: FileRecord[]) => {
          await loadAnalysis();
        }}
      />

      <div className="card">
        <h3>Arquivos enviados</h3>
        {analysis.files.filter((file) => file.category === "input").length ? (
          <ul className="plain-list">
            {analysis.files
              .filter((file) => file.category === "input")
              .map((file) => (
                <li key={file.id}>
                  {file.original_name} ({Math.round(file.size_bytes / 1024)} KB)
                </li>
              ))}
          </ul>
        ) : (
          <p className="muted">Nenhum FASTQ enviado ainda.</p>
        )}
        <div className="button-row">
          <button onClick={submitJob}>Submeter análise</button>
          {job?.status === "pending" ? (
            <button className="secondary-button button-inline" onClick={cancelPendingJob}>
              Cancelar job pendente
            </button>
          ) : null}
        </div>
      </div>

      <div className="card">
        <h3>Status do job</h3>
        {job ? (
          <>
            <p><strong>Status:</strong> <StatusBadge status={job.status} /></p>
            <p><strong>Início:</strong> {job.started_at || "-"}</p>
            <p><strong>Fim:</strong> {job.finished_at || "-"}</p>
            <p><strong>Exit code:</strong> {job.exit_code ?? "-"}</p>
            <p><strong>Erro:</strong> {job.error_message || "-"}</p>
          </>
        ) : (
          <p className="muted">Nenhum job criado ainda.</p>
        )}
      </div>

      <div className="card">
        <h3>Reprocessamento</h3>
        <label>
          Pipeline para nova execução
          <select value={reprocessPipeline} onChange={(event) => setReprocessPipeline(event.target.value)}>
            {pipelines.map((pipeline) => (
              <option key={pipeline.name} value={pipeline.name}>
                {pipeline.name} ({pipeline.version})
              </option>
            ))}
          </select>
        </label>
        <div className="button-row">
          <button
            onClick={reprocessJob}
            disabled={job ? ["pending", "downloading", "running", "uploading_results"].includes(job.status) : false}
          >
            Reprocessar
          </button>
        </div>
        {job && ["pending", "downloading", "running", "uploading_results"].includes(job.status) ? (
          <p className="muted">Aguarde o job atual terminar antes de criar uma nova execução.</p>
        ) : null}
      </div>

      <div className="card">
        <h3>Logs resumidos</h3>
        {job?.logs.length ? (
          <pre className="log-view">
            {job.logs.map((entry) => `[${entry.created_at}] ${entry.level.toUpperCase()} ${entry.message}`).join("\n")}
          </pre>
        ) : (
          <p className="muted">Sem logs ainda.</p>
        )}
      </div>

      <div className="card">
        <h3>Resultados</h3>
        <ResultList files={resultFiles} apiBaseUrl={apiBaseUrl} />
      </div>
    </div>
  );
}
