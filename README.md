<<<<<<< HEAD
# Beverage Bottle Vision & Continual Learning System

A production-oriented API system for detecting bottles inside transparent beverage refrigerators and identifying exact product SKUs with continual learning and catastrophic forgetting protection.

---

## Architecture Overview

The system uses a modular decoupled pipeline:

```
Client Image
   │
   ▼
FastAPI Prediction Service
   ├── Object Detector (Localize bottles / bounding boxes)
   ├── Crop Processor (Extract bottle crops)
   ├── SKU Classifier (Classify exact SKU with top-k confidence)
   └── SKU Registry (Lookup brand, category, volume, packaging)
   │
   ▼
Confidence Routing & Human Review Queue
   │
   ▼
Training Queue + Class-Balanced Replay Buffer
   │
   ▼
Continual / Incremental Learning Worker
   │
   ▼
Validation on Fixed Benchmark Dataset
   ├── PASS -> Atomic Production Model Deployment & Versioning
   └── FAIL -> Reject Candidate Model (Retain Current Production)
```

---

## Phase 1 Implementation Summary

- **Project Structure**: Clean modular architecture with strict separation of concerns (`app/api`, `app/services`, `app/models`, `app/db`, `app/ml`, `app/utils`).
- **SKU Registry**: Primary classification entity with extensible JSON metadata, brand derivation, and active status filtering.
- **Database Layer**: SQLAlchemy 2.0 ORM models for `SKU`, `Image`, `Detection`, `Prediction`, `Feedback`, `TrainingSample`, `TrainingJob`, and `ModelVersion`.
- **FastAPI Core**: Request ID tracing, structured logging, CORS middleware, lifespan events, and error handling.
- **ML Interfaces**: Clean abstractions (`BaseDetector`, `BaseClassifier`) allowing model swaps (YOLO, ViT, CLIP, embedding search).
- **Configuration**: Pydantic Settings supporting environment overrides for thresholds and paths.
- **Automated Tests**: Pytest test suite covering endpoints, SKU operations, and database integrity.

---

## Quickstart & Setup

### 1. Prerequisites
- Python 3.10+
- Virtual environment tool (`venv` or `conda`)

### 2. Environment Setup
```bash
# Create and activate virtual environment
python -m venv .venv
# On Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# On Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Running the Application
Make sure you are in the project root directory (`pratyush/`).

**Option A (Using Python module from virtual environment - Recommended on Windows):**
```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Option B (After activating virtual environment):**
```powershell
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Interactive API documentation will be available at:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## API Endpoints (Phase 1)

| Method | Path | Description |
|---|---|---|
| `GET` | `/` | Root information and documentation links |
| `GET` | `/health` | Application status & database connectivity check |
| `GET` | `/skus` | List registered SKUs with filtering (`brand`, `category`, `active`) |
| `POST` | `/skus` | Register a new unique SKU |
| `GET` | `/skus/{sku_id}` | Retrieve details of a specific SKU |
| `PUT` | `/skus/{sku_id}` | Update SKU metadata |
| `DELETE` | `/skus/{sku_id}` | Remove an SKU from the registry |

---

## Running Tests

Execute the automated test suite with `pytest`:

```powershell
.\.venv\Scripts\python.exe -m pytest -v
```

---

## Roadmap

- **Phase 1 (Completed)**: Core structure, configuration, database schema, SKU registry, FastAPI skeleton, health check, unit tests.
- **Phase 2**: Implement `/predict` with mock detector and classifier pipeline.
- **Phase 3**: Implement `/feedback` and review queue mechanism.
- **Phase 4**: Implement training queue and class-balanced replay buffer.
- **Phase 5**: Implement model versioning, validation benchmarks, and rollback.
- **Phase 6-8**: Integrate object detector, ViT/CNN classifier, and continual learning worker.
- **Phase 9**: End-to-end integration and containerization.
=======
# sample
>>>>>>> 7c82ac55d928a5fd258ef348492495be9e7084a2
