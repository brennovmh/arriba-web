import { FormEvent, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";
import { PipelineDefinition } from "../types";

export default function NewAnalysisPage() {
  const navigate = useNavigate();
  const [pipelines, setPipelines] = useState<PipelineDefinition[]>([]);
  const [form, setForm] = useState({
    name: "",
    sample_id: "",
    project_name: "",
    notes: "",
    pipeline_name: "dummy-ngs",
  });

  useEffect(() => {
    api.get<PipelineDefinition[]>("/pipelines").then((response) => {
      setPipelines(response.data);
      if (response.data.length > 0) {
        setForm((current) => ({ ...current, pipeline_name: response.data[0].name }));
      }
    });
  }, []);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    const response = await api.post("/analyses", form);
    navigate(`/analyses/${response.data.id}`);
  }

  return (
    <div className="card">
      <h2>Nova análise</h2>
      <form className="stack-form" onSubmit={handleSubmit}>
        <label>
          Nome da análise
          <input value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} required />
        </label>
        <label>
          Identificador da amostra
          <input
            value={form.sample_id}
            onChange={(event) => setForm({ ...form, sample_id: event.target.value })}
            required
          />
        </label>
        <label>
          Projeto
          <input
            value={form.project_name}
            onChange={(event) => setForm({ ...form, project_name: event.target.value })}
          />
        </label>
        <label>
          Observações
          <textarea value={form.notes} onChange={(event) => setForm({ ...form, notes: event.target.value })} />
        </label>
        <label>
          Pipeline
          <select
            value={form.pipeline_name}
            onChange={(event) => setForm({ ...form, pipeline_name: event.target.value })}
          >
            {pipelines.map((pipeline) => (
              <option key={pipeline.name} value={pipeline.name}>
                {pipeline.name} ({pipeline.version})
              </option>
            ))}
          </select>
        </label>
        <button type="submit">Criar análise</button>
      </form>
    </div>
  );
}
