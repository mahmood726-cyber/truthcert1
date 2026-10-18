
## Installation
The submission converter resolves inputs beside PLOS_ONE_Submission/convert_files.py.
ZIP creation needs only the Python standard library. DOCX/PDF/image conversion
loads python-docx, fpdf2 or Pillow only when that conversion is requested.
ZIP inputs must all exist and have unique member names. A failed write preserves
the previous archive instead of silently publishing an incomplete replacement.
Rebuild the production JavaScript with `npm ci` then `npm run build:min`.
The locked Terser formatter removes whitespace/comments without compression or
name mangling. The statistical source in app.js is unchanged. Syntax tests guard
both the readable source and production artifact against startup failures.

Use the dependency files in this directory (for example `requirements.txt`, `environment.yml`, `DESCRIPTION`, or equivalent project-specific files) to create a clean local environment before running analyses.
Document any package-version mismatch encountered during first run.

TruthCert Africa Packs v1 (schema-first)

- 13 countries x 7 disease groups.
- Pairwise-only.
- Local currency (LCU) output always.

Start here:
- index.yaml
- countries/<ISO3>.yaml
- diseases/<GROUP>.yaml
- country_disease/<ISO3>__<GROUP>.yaml
