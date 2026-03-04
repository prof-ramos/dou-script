# Architecture Overview

## 1. Project Structure
```
dou-script/
├── src/                    # Source code directory
│   └── dou_script/        # Main package
│       ├── __init__.py     # Package initialization
│       ├── main.py         # Application entry point
│       ├── models/         # Data models
│       ├── views/          # Web views (Django/Flask)
│       ├── api/            # API endpoints
│       ├── services/       # Business logic
│       ├── utils/          # Utility functions
│       └── config/         # Configuration files
├── tests/                  # Test files
│   ├── __init__.py
│   ├── conftest.py        # pytest configuration
│   ├── test_models.py
│   ├── test_views.py
│   └── test_utils.py
├── requirements/           # Dependency files
│   ├── base.txt           # Production dependencies
│   ├── dev.txt            # Development dependencies
│   └── prod.txt           # Production dependencies
├── .venv/                 # Virtual environment
├── docs/                  # Documentation directory
│   ├── ARQUITETURA.md     # Detailed architecture documentation
│   ├── DIAGRAMA.md        # System diagrams
│   └── VISAO_GERAL.md     # System overview
├── public/                # Public resources
│   ├── bash/              # Shell scripts
│   └── python/            # Python scripts
├── output/                # Downloaded and processed files
├── ARCHITECTURE.md        # This architecture overview
├── CLAUDE.md              # Development guidelines
├── README.md              # Project overview
└── cron-dou.sh            # Cron job wrapper
```

## 2. High-Level System Architecture

### System Overview
The DOU Script is an automated system for downloading and filtering the Diário Oficial da União (DOU), focusing on content from the Ministry of Foreign Affairs (MRE). The system follows a scheduled batch processing model with three main components:

```
┌─────────────────────────────────────────────────────────────┐
│                    CAMADA DE AGENDAMENTO                    │
│                      (cron + shell)                         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                 CAMADA DE PROCESSAMENTO                     │
│                   (Python + requests)                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │ Autenticação │  │   Download   │  │  Filtragem   │    │
│  │   IN Labs    │  │   XML/ZIP    │  │     MRE      │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  CAMADA DE ARMAZENAMENTO                    │
│              (output/ + arquivos temporários)               │
└─────────────────────────────────────────────────────────────┘
```

### Detailed Architecture Documentation
For detailed technical architecture, system diagrams, and implementation specifics, see:

- **[docs/ARQUITETURA.md](./docs/ARQUITETURA.md)** - Detailed architecture document with complete system specifications
- **[docs/DIAGRAMA.md](./docs/DIAGRAMA.md)** - System diagrams and flow charts
- **[docs/VISAO_GERAL.md](./docs/VISAO_GERAL.md)** - System overview and vision

## 3. Core Components

### 3.1 Main Entry Point (`main.py`)
- **Purpose:** Application initialization and orchestration
- **Responsibilities:**
  - Parse command-line arguments
  - Configure logging
  - Initialize services
  - Execute download pipeline
  - Handle errors and exceptions

### 3.2 Processing Layer (`public/python/`)
The main processing logic is organized in the `public/python/` directory:

- **`inlabs-filter-mre.py`** - Main script for DOU download and MRE filtering
- **`inlabs-auto-download-*.py`** - Additional download utilities

### 3.3 Scheduling Layer (`cron-dou.sh`)
- **Purpose:** Automated execution orchestration
- **Responsibilities:**
  - Environment variable setup
  - Script execution at scheduled times
  - Error handling and logging

### 3.4 Output Layer (`output/`)
- **Purpose:** Store processed results
- **Structure:**
  - `YYYY-MM-DD-SEÇÃO-MRE.txt` - Filtered content files
  - Timestamp-based organization
  - Automatic cleanup management

## 4. Data Flow

### 4.1 Download Process
1. **Cron Trigger** - Scheduled execution at 10:00 AM (Mon-Fri)
2. **Authentication** - Login to IN Labs API via session cookie
3. **Download** - Fetch XML/ZIP files for all DOU sections
4. **Processing** - Extract and clean XML content
5. **Filtering** - Apply MRE keyword filtering
6. **Storage** - Save filtered results to output directory

### 4.2 Duplicate Management
- **12:00 PM & 11:00 PM** - Check for duplicate publications
- **Automatic Cleanup** - Remove redundant files
- **Day-end Finalization** - Ensure complete day processing

## 5. External Integrations

### 5.1 IN Labs API
- **URL:** https://inlabs.in.gov.br
- **Authentication:** Session-based (email/password)
- **Rate Limits:** Respect API constraints
- **Error Handling:** 404 treated as normal (no publication)

### 5.2 File System
- **Local Storage:** Downloaded and processed files
- **Directory Structure:** Organized by date and section
- **Cleanup:** Automatic duplicate management

### 5.3 Cron Scheduler
- **Schedule:** Multiple daily executions
- **Environment:** Linux/Unix cron daemon
- **Monitoring:** Process health checks

## 6. Security Considerations

### 6.1 Authentication Security
- **Credentials Storage:** Environment variables (.env)
- **Session Management:** Cookie-based authentication
- **Access Control:** File permissions management

### 6.2 Data Security
- **Input Validation:** XML content sanitization
- **Error Handling:** Secure error message handling
- **Backup Procedures:** Regular data backup

## 7. Development Environment

### 7.1 Testing Framework
- **Framework:** pytest
- **Coverage:** 94% test coverage
- **Test Files:** 37 test cases
- **Categories:** Unit, integration, and E2E tests

### 7.2 Code Quality Tools
- **Formatting:** Black
- **Import Sorting:** isort
- **Linting:** flake8
- **Type Checking:** mypy

### 7.3 Development Commands
```bash
# Environment setup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Testing
pytest --cov=src
pytest --cov-report=html

# Code quality
black .
isort .
flake8 src/
mypy src/
```

## 8. Deployment

### 8.1 Local Development
- **Requirements:** Python 3.8+, virtual environment
- **Setup:** Manual environment configuration
- **Execution:** Direct script execution

### 8.2 Production Deployment
- **Infrastructure:** Linux server (Ubuntu/Debian)
- **Scheduling:** Cron-based automation
- **Monitoring:** Manual process monitoring
- **Storage:** Local file system

## 9. Technology Stack

### 9.1 Core Technologies
- **Python 3.8+** - Programming language
- **requests** - HTTP client library
- **pytest** - Testing framework
- **venv** - Virtual environment

### 9.2 Processing Libraries
- **zipfile** - ZIP file processing
- **xml.etree.ElementTree** - XML parsing
- **re** - Regular expressions
- **datetime** - Date/time handling

### 9.3 Development Tools
- **Black** - Code formatter
- **isort** - Import organizer
- **flake8** - Linter
- **mypy** - Type checker

## 10. Future Enhancements

### 10.1 Short Term (1-3 months)
- Enhanced error recovery mechanisms
- Improved monitoring and alerting
- Configuration system flexibility

### 10.2 Medium Term (3-6 months)
- Database integration (SQLite/PostgreSQL)
- Web dashboard interface
- Email notification system

### 10.3 Long Term (6-12 months)
- Cloud deployment options
- Distributed processing capabilities
- Multi-format support
- Mobile application interface

## 11. Documentation Structure

### 11.1 Core Documentation
- **ARCHITECTURE.md** - This overview document
- **docs/ARQUITETURA.md** - Detailed technical architecture
- **docs/DIAGRAMA.md** - System diagrams and flows
- **docs/VISAO_GERAL.md** - System vision and overview

### 11.2 Development Guidelines
- **CLAUDE.md** - Development best practices and guidelines
- **README.md** - Project overview and quick start

### 11.3 Additional Resources
- **public/bash/** - Shell scripts and utilities
- **public/python/** - Python processing scripts
- **requirements/** - Dependency management files

---

**Last Updated:** 2026-03-04
**Status:** Production
**Version:** 1.0.0