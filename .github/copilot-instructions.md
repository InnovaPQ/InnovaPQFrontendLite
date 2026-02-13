## Quick orientation for AI coding agents

This repository is a small Streamlit-based MVP that collects PQ (power quality) inputs, uploads them to AWS S3, triggers processing (via SQS / external worker), and renders a report UI.

Key files
- `frontPage.py` — Streamlit uploader UI. Responsible for collecting user metadata and 7 input files. Uploads files to S3 under `reports/{report_id}/inputs/` and sends an SQS message with the `report_id` and S3 prefixes.
- `codigoRed.py` — Streamlit report viewer. Reads Excel/PNG assets from local `input/` and `out/` folders (see `DB_Origen` dict). Shows tables, descriptions and images. Uses `init_aws_clients()` but mainly reads local file paths.
- `aws_client.py` — AWS client initialization. Exposes `init_aws_clients()`, `AWS_S3_BUCKET_NAME`, and `AWS_SQS_QUEUE_URL`. The constants are placeholders and must be configured for real AWS access.
- `requirements.txt` — declared deps, but note: code imports `openpyxl` and `fpdf` which are not listed here. Also `boto3` and `streamlit` are required.

High-level architecture and data flow (concise)
- User uploads inputs via `frontPage.py` → files uploaded to S3 key `reports/{report_id}/inputs/`.
- `frontPage.py` sends an SQS message with `report_id`, `s3_input_prefix`, and `s3_output_prefix` to trigger asynchronous processing (a Lambda or worker outside this repo).
- The processing stage (external) is expected to produce output files under `reports/{report_id}/outputs/` (or copy results into the app's `out/` folders). `codigoRed.py` currently expects outputs to be present under `out/...` and reads Excel files locally.

Project-specific conventions and patterns
- DB_Origen mapping: `codigoRed.py` centralizes expected input/output paths in a `DB_Origen` dict. Follow this pattern when adding new report assets.
- UI language and labels are Spanish. Keep new UI text consistent with Spanish strings.
- File reading patterns: use `pandas.read_excel(io=path)` and assume the first row may contain a title (see `Descripciones.ConstruirContenedor`). New Excel generation should follow this layout.
- Upload behavior: `frontPage.py` uses `s3_client.upload_fileobj(file_obj, AWS_S3_BUCKET_NAME, s3_key)` — use the original filename when constructing S3 keys.

Integration points and external dependencies to watch
- S3 bucket and SQS queue: `aws_client.py` has placeholders. For local development, either set environment AWS creds or stub `boto3` calls. The app checks `aws_configured` and shows Streamlit errors when AWS is not available.
- External processor: The repo expects an out-of-repo processing step (Lambda/worker) that consumes the SQS message and writes results to S3 (or the app's `out/` dirs). There is no worker code in this repo.

Known gaps and cautions for edits
- `codigoRed.py` references undefined symbols/functions: e.g., `create_pdf`, `mock_image_url_1`, `mock_image_url_2`. If you implement PDF export, update or add a helper module and tests.
- `requirements.txt` is incomplete versus imports. Add `openpyxl` and `fpdf` if you change or run `codigoRed.py` locally.
- `codigoRed.py` reads files from `out/` and `input/` folders — when testing locally, populate those folders or mock file I/O.

How to run locally (Windows PowerShell examples)
- Install dependencies: `pip install -r requirements.txt` (add missing libs first if needed: `pip install openpyxl fpdf`).
- Run uploader: `streamlit run frontPage.py`.
- Run report viewer: `streamlit run codigoRed.py`.

Small examples to reference in edits
- Use `s3_client.upload_fileobj(file_obj, AWS_S3_BUCKET_NAME, s3_key)` (see `frontPage.py`) for streaming uploads.
- Check `aws_configured` after `init_aws_clients()` before calling AWS APIs.
- Reuse `DB_Origen` when adding new report sections to keep UI wiring consistent.

If merging with an existing `.github/copilot-instructions.md`
- Preserve any project-specific directives already present. Only add or update the sections above (Key files, Data flow, Conventions, Gaps, Run steps).

If anything above is unclear or you want the doc adapted for a different agent persona (unit-test writer, refactorer, or security reviewer), tell me which persona and I will refine the file.
