import { getToken } from "../services/auth";
import { FileRecord } from "../types";

type Props = {
  files: FileRecord[];
  apiBaseUrl: string;
};

export default function ResultList({ files, apiBaseUrl }: Props) {
  const token = getToken();
  if (!files.length) {
    return <p className="muted">Nenhum output final registrado ainda.</p>;
  }

  return (
    <div className="result-grid">
      {files.map((file) => (
        <div className="result-card" key={file.id}>
          <strong>{file.original_name}</strong>
          <span className="muted">{file.category}</span>
          <span className="muted">{Math.round(file.size_bytes / 1024)} KB</span>
          <a href={`${apiBaseUrl}/files/${file.id}/download?access_token=${token || ""}`} target="_blank" rel="noreferrer">
            Download
          </a>
          {file.previewable && file.file_type !== "pdf" ? (
            <img
              alt={file.original_name}
              src={`${apiBaseUrl}/files/${file.id}/download?access_token=${token || ""}`}
              className="preview-image"
            />
          ) : null}
          {file.previewable && file.file_type === "pdf" ? (
            <a href={`${apiBaseUrl}/files/${file.id}/download?access_token=${token || ""}`} target="_blank" rel="noreferrer">
              Abrir PDF
            </a>
          ) : null}
        </div>
      ))}
    </div>
  );
}
