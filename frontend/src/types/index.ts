export type FileRecord = {
  id: number;
  analysis_id: number;
  job_id: number | null;
  file_type: string;
  category: string;
  original_name: string;
  stored_name: string;
  relative_path: string;
  size_bytes: number;
  checksum: string | null;
  previewable: boolean;
  created_at: string;
};

export type JobLog = {
  id: number;
  level: string;
  message: string;
  created_at: string;
};

export type Job = {
  id: number;
  analysis_id: number;
  status: string;
  worker_id: number | null;
  pipeline_name: string;
  pipeline_version: string;
  input_manifest_json: Record<string, unknown>;
  output_manifest_json: { items?: OutputManifestItem[] };
  error_message: string | null;
  exit_code: number | null;
  started_at: string | null;
  finished_at: string | null;
  created_at: string;
  updated_at: string;
};

export type JobDetails = Job & {
  files: FileRecord[];
  logs: JobLog[];
};

export type Analysis = {
  id: number;
  name: string;
  sample_id: string;
  project_name: string | null;
  notes: string | null;
  pipeline_name: string;
  created_by: number;
  created_at: string;
  updated_at: string;
  latest_job: Job | null;
  files: FileRecord[];
};

export type OutputManifestItem = {
  friendly_name: string;
  relative_path: string;
  file_type: string;
  size: number;
  category: string;
  previewable: boolean;
  checksum?: string;
};

export type PipelineDefinition = {
  name: string;
  version: string;
  description: string;
};
