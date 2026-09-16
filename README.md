# TrustCatalog — AI-Powered E-Commerce Catalog Integrity & Early-Warning System

TrustCatalog is an evidence-first catalog auditor for e-commerce platforms. It analyzes seller and seller-product behavior, detects abnormal fulfillment patterns, ranks risk, and explains the numerical evidence behind each alert.

> **Dataset:** Brazilian E-Commerce Public Dataset by Olist, a public dataset of about 100k orders from 2016–2018. The dataset is historical and anonymized. The project does not claim that the Olist data contains a direct ghost-listing label.

## What the prototype demonstrates

- Seller-level behavioral feature engineering.
- Historical-vs-recent deterioration analysis.
- Delivery-delay and late-delivery signals.
- Observed `canceled` / `unavailable` fulfillment signals.
- Isolation Forest anomaly detection.
- Transparent 0–100 weighted risk score.
- Six cooperating agents plus an Orchestrator.
- Evidence-grounded explanations.
- Controlled stress test that degrades derived features **in memory** without modifying raw Olist data.
- FastAPI API and responsive React dashboard.

## Architecture

```text
Olist CSVs
   |
   v
Data Loader / Validation
   |
   v
Feature Engineering
   |-------------------|--------------------|-------------------|
   v                   v                    v                   v
Seller Behavior    Shipping Agent    Order Reliability    Anomaly Agent
   |                   |                    |                   |
   +-------------------+--------------------+-------------------+
                               |
                               v
                       Risk Aggregator
                               |
                               v
                       Explanation Agent
                               |
                               v
                         FastAPI API
                               |
                               v
                       React Dashboard
```

## Risk score

The final score is reproducible and stored as components:

`Risk = 100 × (0.25×cancellation + 0.20×shipping + 0.20×fulfillment + 0.25×deterioration + 0.10×anomaly)`

Each component is normalized to `[0,1]`. Risk levels are:

- 0–39: LOW
- 40–69: MEDIUM
- 70–100: HIGH

The weights are configuration, not an ML claim; they can be tuned and evaluated on the controlled stress test.

## Why time matters

Lifetime averages can hide deterioration. TrustCatalog creates an earlier baseline window and a recent window, then calculates changes in cancellation, unavailability, fulfillment failure, lateness, delivery delay, and review score.

## Dataset setup

The canonical public source is Olist's Kaggle dataset.https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce

If the dataset is already present in `data/raw`, do not run the download script. Otherwise:

```bash
pip install -r requirements.txt
pip install kaggle
python scripts_download_data.py
```

The download script uses the public Kaggle dataset and refuses to download if any expected raw file is already present.

## Run backend

From the project root:

```bash
python -m pip install -r requirements.txt
uvicorn backend.main:app --reload --port 8000
```

The first API call loads the Olist files and computes features. With the full dataset this is intentionally a local batch-style prototype, not a production streaming service.

## Run frontend

```bash
cd frontend
npm install
npm run dev
```

Open the Vite URL shown in the terminal.

## Pipeline output

```bash
python -m backend.run_pipeline
```

Outputs:

- `data/processed/dataset_inventory.csv`
- `data/processed/seller_features.parquet`
- `data/processed/listing_features.parquet`

## API

- `GET /api/health`
- `GET /api/overview`
- `GET /api/sellers?limit=100`
- `GET /api/sellers/{seller_id}`
- `GET /api/risk-ranking?limit=100`
- `GET /api/agents/{seller_id}`
- `POST /api/stress-test`
- `GET /api/evaluation`

## Stress test

The stress test selects real sellers from Olist, copies the derived feature table in memory, applies controlled degradation to recent cancellation/failure/delay signals, reruns Isolation Forest and the same risk pipeline, and checks how many degraded sellers appear in the resulting top-K ranking.

The original CSVs are never changed. The UI explicitly labels the result as a simulation.

The reported detection metrics are computed at runtime. No success number is hard-coded.

## Evaluation

Because the original Olist dataset has no direct ghost-listing ground truth, real-world precision/recall for ghost listings cannot honestly be claimed from this dataset alone. The controlled stress test supplies known simulated labels. Report:

- detection rate in the chosen top-K;
- Precision@K when the stress-test population defines the positive class;
- false-positive rate over the chosen simulation population;
- score movement before vs. after degradation.

## Testing

```bash
pytest -q
```

Tests cover risk-score bounds and stress-test transformation behavior without requiring the full Olist dataset.

## Limitations

1. Olist is historical 2016–2018 data, not a live inventory feed.
2. There is no inventory snapshot and no direct ghost-listing label, so the stress-test scenario is simulated.
3. Seller attribution is inferred from order items; an order with multiple sellers is attributed to the first seller only for seller-level order metrics. Seller-product features retain the true item-level relationship.
4. Sparse sellers have less reliable recent/baseline comparisons; missing periods are treated conservatively.
5. Isolation Forest is used for behavioral novelty, not as proof of wrongdoing.
6. The explanation layer is deterministic in the MVP so it cannot invent numerical evidence. An optional LLM adapter can be added later with strict structured-input grounding.

## Future improvements

- event-stream ingestion for real inventory/availability snapshots;
- survival/time-to-failure modeling;
- seller-product temporal anomaly detection;
- calibrated supervised model once real failure labels exist;
- human feedback loop for alert outcomes;
- optional local/open-weight LLM explanation adapter with schema validation;
- SQLite/Parquet caching for faster repeated dashboard loads.

## Phone-friendly deployment

### 1. GitHub
The repository must contain the actual folders:
`backend/`, `frontend/`, `data/`, `tests/`, `docs/`.

Do not upload only the ZIP file. Extract this ZIP first, then upload the extracted project contents to GitHub.

### 2. Dataset
The Olist CSV files are intentionally not bundled into this ZIP. Put the nine required CSV files under:
`data/raw/`

Do not replace them with fabricated data.

### 3. Backend
Deploy `trustcatalog-api` with:
- Build: `pip install -r requirements.txt`
- Start: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`

Set `FRONTEND_ORIGIN` to the deployed frontend URL.

### 4. Frontend
Deploy the `frontend/` directory as a Vite site.
Set:
`VITE_API_URL=https://YOUR-BACKEND-URL/api`

Build command:
`npm install && npm run build`

Publish directory:
`dist`

### 5. Important
The first API request computes the feature pipeline from the Olist files, so the backend needs access to `data/raw/`.
