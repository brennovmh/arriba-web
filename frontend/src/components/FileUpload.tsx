import { ChangeEvent, useState } from "react";
import api from "../services/api";
import { FileRecord } from "../types";

type Props = {
  analysisId: number;
  onUploaded: (files: FileRecord[]) => void;
};

export default function FileUpload({ analysisId, onUploaded }: Props) {
  const [progress, setProgress] = useState<number>(0);
  const [busy, setBusy] = useState(false);

  async function handleUpload(event: ChangeEvent<HTMLInputElement>) {
    const selectedFiles = event.target.files;
    if (!selectedFiles?.length) {
      return;
    }
    const formData = new FormData();
    Array.from(selectedFiles).forEach((file) => formData.append("files", file));
    setBusy(true);
    setProgress(0);
    const response = await api.post<FileRecord[]>(`/analyses/${analysisId}/upload`, formData, {
      headers: { "Content-Type": "multipart/form-data" },
      onUploadProgress: (evt) => {
        if (!evt.total) {
          return;
        }
        setProgress(Math.round((evt.loaded / evt.total) * 100));
      },
    });
    onUploaded(response.data);
    setBusy(false);
  }

  return (
    <div className="card">
      <h3>Upload de FASTQ</h3>
      <input type="file" multiple onChange={handleUpload} accept=".fastq,.fastq.gz,.fq,.fq.gz" />
      {busy ? <p className="muted">Enviando: {progress}%</p> : null}
    </div>
  );
}
