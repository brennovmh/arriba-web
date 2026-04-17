from __future__ import annotations

import argparse
import json
from pathlib import Path
import time
import zipfile

from PIL import Image, ImageDraw


def make_png(target: Path, title: str, color: str) -> None:
    image = Image.new("RGB", (900, 480), color=color)
    draw = ImageDraw.Draw(image)
    draw.rectangle((40, 40, 860, 440), outline="white", width=4)
    draw.text((70, 80), title, fill="white")
    draw.text((70, 150), "Dummy pipeline output for MVP validation", fill="white")
    image.save(target)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pipeline-name", required=True)
    parser.add_argument("--metadata", required=True)
    parser.add_argument("--input-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--refs-dir", required=True)
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    refs_dir = Path(args.refs_dir)
    metadata = json.loads(Path(args.metadata).read_text(encoding="utf-8"))

    if not refs_dir.exists():
        raise SystemExit("Reference directory not found")
    fastqs = sorted([path for path in input_dir.iterdir() if path.is_file()])
    if not fastqs:
        raise SystemExit("No FASTQ files found")

    logs_dir = output_dir / "logs"
    plots_dir = output_dir / "plots"
    reports_dir = output_dir / "reports"
    tables_dir = output_dir / "tables"
    for path in [logs_dir, plots_dir, reports_dir, tables_dir]:
        path.mkdir(parents=True, exist_ok=True)

    pipeline_log = logs_dir / "dummy_steps.log"
    with pipeline_log.open("w", encoding="utf-8") as handle:
        handle.write(f"Pipeline: {args.pipeline_name}\n")
        handle.write(f"Sample: {metadata['analysis_metadata']['sample_id']}\n")
        handle.write("Step 1/3: input validation\n")
        time.sleep(1)
        handle.write("Step 2/3: simulated QC aggregation\n")
        time.sleep(1)
        handle.write("Step 3/3: rendering outputs\n")

    summary_path = tables_dir / "summary.tsv"
    with summary_path.open("w", encoding="utf-8") as handle:
        handle.write("sample_id\tfastq_count\ttotal_size_bytes\tpipeline\n")
        handle.write(
            f"{metadata['analysis_metadata']['sample_id']}\t{len(fastqs)}\t"
            f"{sum(item.stat().st_size for item in fastqs)}\t{args.pipeline_name}\n"
        )

    make_png(plots_dir / "coverage.png", "Coverage Summary", "#115e59")
    make_png(plots_dir / "qc_plot.png", "QC Plot", "#1d4ed8")

    report_path = reports_dir / "report.html"
    report_path.write_text(
        f"""
        <html>
          <body>
            <h1>Dummy NGS Report</h1>
            <p>Analysis: {metadata['analysis_metadata']['analysis_name']}</p>
            <p>Sample: {metadata['analysis_metadata']['sample_id']}</p>
            <ul>
              <li>FASTQ files: {len(fastqs)}</li>
              <li>Pipeline: {args.pipeline_name}</li>
              <li>Refs dir: {refs_dir}</li>
            </ul>
          </body>
        </html>
        """.strip(),
        encoding="utf-8",
    )

    package_path = output_dir / "package.zip"
    with zipfile.ZipFile(package_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for file_path in [summary_path, report_path, plots_dir / "coverage.png", plots_dir / "qc_plot.png", pipeline_log]:
            archive.write(file_path, arcname=str(file_path.relative_to(output_dir)))


if __name__ == "__main__":
    main()
