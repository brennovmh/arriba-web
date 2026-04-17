from sqlalchemy.orm import Session, joinedload

from app.models import Analysis, FileRecord, Job
from app.schemas.analysis import AnalysisCreate
from app.services.pipeline_service import get_pipeline_or_400


def list_analyses_for_user(db: Session, user_id: int) -> list[Analysis]:
    analyses = (
        db.query(Analysis)
        .options(joinedload(Analysis.files), joinedload(Analysis.jobs))
        .filter(Analysis.created_by == user_id)
        .order_by(Analysis.created_at.desc())
        .all()
    )
    return analyses


def create_analysis(db: Session, payload: AnalysisCreate, user_id: int) -> Analysis:
    get_pipeline_or_400(payload.pipeline_name)
    analysis = Analysis(
        name=payload.name,
        sample_id=payload.sample_id,
        project_name=payload.project_name,
        notes=payload.notes,
        pipeline_name=payload.pipeline_name,
        created_by=user_id,
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    return analysis


def get_analysis_for_user(db: Session, analysis_id: int, user_id: int) -> Analysis | None:
    return (
        db.query(Analysis)
        .options(joinedload(Analysis.files), joinedload(Analysis.jobs))
        .filter(Analysis.id == analysis_id, Analysis.created_by == user_id)
        .first()
    )


def _build_input_manifest(analysis: Analysis) -> dict:
    return {
        "analysis_id": analysis.id,
        "sample_id": analysis.sample_id,
        "files": [
            {
                "file_id": f.id,
                "original_name": f.original_name,
                "relative_path": f.relative_path,
                "size_bytes": f.size_bytes,
                "checksum": f.checksum,
            }
            for f in analysis.files
            if f.category == "input"
        ],
    }


def create_or_reset_job(db: Session, analysis: Analysis) -> Job:
    latest_job = (
        db.query(Job).filter(Job.analysis_id == analysis.id).order_by(Job.created_at.desc()).first()
    )
    manifest = _build_input_manifest(analysis)

    if latest_job and latest_job.status in {"failed", "completed", "cancelled"}:
        pipeline = get_pipeline_or_400(analysis.pipeline_name)
        job = Job(
            analysis_id=analysis.id,
            status="pending",
            pipeline_name=analysis.pipeline_name,
            pipeline_version=pipeline["version"],
            input_manifest_json=manifest,
            output_manifest_json={"items": []},
        )
    elif latest_job:
        return latest_job
    else:
        pipeline = get_pipeline_or_400(analysis.pipeline_name)
        job = Job(
            analysis_id=analysis.id,
            status="pending",
            pipeline_name=analysis.pipeline_name,
            pipeline_version=pipeline["version"],
            input_manifest_json=manifest,
            output_manifest_json={"items": []},
        )

    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def create_reprocess_job(db: Session, analysis: Analysis, pipeline_name: str | None = None) -> Job:
    selected_pipeline = pipeline_name or analysis.pipeline_name
    pipeline = get_pipeline_or_400(selected_pipeline)
    latest_job = (
        db.query(Job).filter(Job.analysis_id == analysis.id).order_by(Job.created_at.desc()).first()
    )
    if latest_job and latest_job.status in {"pending", "downloading", "running", "uploading_results"}:
        raise ValueError("Cannot reprocess while the latest job is still active")

    analysis.pipeline_name = selected_pipeline
    job = Job(
        analysis_id=analysis.id,
        status="pending",
        pipeline_name=selected_pipeline,
        pipeline_version=pipeline["version"],
        input_manifest_json=_build_input_manifest(analysis),
        output_manifest_json={"items": []},
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def latest_job_for_analysis(analysis: Analysis) -> Job | None:
    if not analysis.jobs:
        return None
    return sorted(analysis.jobs, key=lambda job: job.created_at, reverse=True)[0]


def result_files_for_job(db: Session, job_id: int) -> list[FileRecord]:
    return db.query(FileRecord).filter(FileRecord.job_id == job_id, FileRecord.category != "input").all()
