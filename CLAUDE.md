# CLAUDE.md — dou-script

## Project Overview

`dou-script` is a collection of scripts (Bash and Python) that automate the download of publications from the Brazilian **Diário Oficial da União (DOU)** — the federal government's Official Gazette — via the **INLABS** platform (`inlabs.in.gov.br`).

The project provides two equivalent implementations of the same workflow (XML/ZIP downloads and PDF downloads) in both languages so users can choose whichever runtime they have available.

---

## Repository Structure

```
dou-script/
├── README.md                          # Empty (top-level placeholder)
└── public/
    ├── bash/
    │   ├── README.md                  # Bash usage instructions (Portuguese)
    │   ├── inlabs-auto-download-xml.sh   # Downloads DOU as XML/ZIP archives
    │   └── inlabs-auto-download-pdf.sh   # Downloads DOU as signed PDF files
    └── python/
        ├── README.md                  # Python usage instructions (Portuguese)
        ├── inlabs-auto-download-xml.py   # Downloads DOU as XML/ZIP archives
        └── inlabs-auto-download-pdf.py   # Downloads DOU as signed PDF files
```

---

## DOU Sections and Naming Conventions

The DOU is divided into sections. Each script accepts a space-separated list of section codes in the `tipo_dou` variable.

### XML/ZIP scripts

| Code  | Meaning                     |
|-------|-----------------------------|
| DO1   | Section 1 (regular edition) |
| DO2   | Section 2 (regular edition) |
| DO3   | Section 3 (regular edition) |
| DO1E  | Section 1 Extra edition     |
| DO2E  | Section 2 Extra edition     |
| DO3E  | Section 3 Extra edition     |

Output filename format: `YYYY-MM-DD-<SECTION>.zip`
Example: `2026-03-04-DO1.zip`

### PDF scripts

| Code | Meaning                                                 |
|------|---------------------------------------------------------|
| do1  | Section 1 (includes all extras, suffixed A–Z)           |
| do2  | Section 2 (includes all extras, suffixed A–Z)           |
| do3  | Section 3 (includes all extras, suffixed A–Z)           |

Main PDF filename: `YYYY_MM_DD_ASSINADO_<section>.pdf`
Extra edition filename: `YYYY_MM_DD_ASSINADO_<section>_extra_<LETTER>.pdf`
Example: `2026_03_04_ASSINADO_do1.pdf`, `2026_03_04_ASSINADO_do1_extra_A.pdf`

> Note: Case matters. XML section codes use uppercase (`DO1`), PDF section codes use lowercase (`do1`).

---

## Authentication Mechanism

All scripts authenticate against INLABS using the same flow:

1. **POST** credentials to `https://inlabs.in.gov.br/logar.php` with:
   - `email` (user login)
   - `password` (user password)
   - Custom header `origem: 736372697074` (required by the API)
2. A successful login sets the session cookie `inlabs_session_cookie`.
3. Subsequent download requests pass this cookie and the same `origem` header.

**Cookie validation**: the scripts check for the presence of `inlabs_session_cookie` before attempting any download and abort if it is missing.

---

## Script Behaviour Details

### Bash scripts

- Write each `curl` command to a temporary `.sh` file, execute it with `sh`, then delete it.
- Store the session in `cookies.iakim` (deleted after the run).
- The PDF script iterates over letters A–Z to probe for extra editions. If a file does not exist on the server, `curl -f` silently fails (no output written).
- Designed to run non-interactively from **cron**.

### Python scripts

- Use the `requests` library with a persistent `requests.Session()` for cookie management.
- Require: `pip install requests` (no other third-party dependencies).
- The XML script handles HTTP 404 gracefully (prints a message and continues).
- The PDF script downloads only the main signed PDF per section (no A–Z extra-edition probing, unlike the Bash equivalent).
- On `ConnectionError` the `login()` function calls itself recursively — be aware of potential unbounded recursion on persistent network failures.
- Run with: `python -W ignore <script>.py` (suppresses SSL warnings).

---

## Configuration

Both languages require editing the script directly before use. There is no external config file or environment variable support.

| Variable   | Location (Bash)        | Location (Python)      | Description                      |
|------------|------------------------|------------------------|----------------------------------|
| `email`    | Line 9 of each `.sh`   | Line 4 of each `.py`   | INLABS account email             |
| `senha`    | Line 10 of each `.sh`  | Line 5 of each `.py`   | INLABS account password          |
| `tipo_dou` | Line 13 of each `.sh`  | Line 7 of each `.py`   | Space-separated list of sections |

**Never commit real credentials.** The placeholder values (`mail@mail.com` / `123456`) must be replaced locally and must not be pushed to version control.

---

## Running the Scripts

### Bash

```bash
chmod +x inlabs-auto-download-xml.sh
./inlabs-auto-download-xml.sh

chmod +x inlabs-auto-download-pdf.sh
./inlabs-auto-download-pdf.sh
```

### Python

```bash
pip install requests
python -W ignore inlabs-auto-download-xml.py
python -W ignore inlabs-auto-download-pdf.py
```

### Cron scheduling (recommended usage)

```
# Example: run at 10:01 every day and log output
01 10 * * * sh /home/user/inlabs-auto-download-xml.sh >> /tmp/inlabs-auto-download-xml.txt
01 10 * * * sh /home/user/inlabs-auto-download-pdf.sh >> /tmp/inlabs-auto-download-pdf.txt
```

---

## Conventions for AI Assistants

- **Language**: Documentation (READMEs, comments) is written in **Brazilian Portuguese**. Code identifiers are also in Portuguese (`senha`, `tipo_dou`, `secao`, etc.).
- **No build system**: there is no Makefile, package.json, pyproject.toml, or any build pipeline. Scripts are standalone and self-contained.
- **No tests**: there is no test suite. Validation is limited to login cookie detection.
- **Credentials must never be committed**: always use placeholder values in source files.
- **Script logic should not be modified without understanding the INLABS API contract**: the `origem` header and cookie name are specific to the platform and must be preserved exactly.
- **Bash temp-file pattern**: the pattern of writing a command to a `.sh` file and executing it is intentional for this version of the scripts; the Python scripts avoid this pattern entirely.
- **Python recursion in `login()`**: the recursive retry on `ConnectionError` has no depth limit — avoid deepening this pattern in any edits.
- **Output files are written to the working directory** from which the script is executed. There is no configurable output path.

---

## Key External Dependency

| Service         | URL                                | Notes                                    |
|-----------------|------------------------------------|------------------------------------------|
| INLABS platform | `https://inlabs.in.gov.br`         | Requires a valid INLABS account          |
| Login endpoint  | `/logar.php`                       | POST with email + password               |
| Download endpoint | `/index.php?p=DATE&dl=FILENAME`  | GET with session cookie + `origem` header |
