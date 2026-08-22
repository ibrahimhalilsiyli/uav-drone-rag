# UAV / Drone Field Maintenance & Flight Operations RAG Assistant

> **Fully offline, production-ready Retrieval-Augmented Generation (RAG) system** for UAV field technicians and flight crews. Zero internet connectivity required after initial model download.

![Python](https://img.shields.io/badge/Python-3.13-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.x-red)
![Foundry Local](https://img.shields.io/badge/Microsoft-Foundry%20Local%20SDK-blue)
![SQLite](https://img.shields.io/badge/Storage-SQLite-green)

---

## Overview

This system provides source-grounded, hallucination-guarded answers for UAV maintenance queries by combining:

- **Microsoft Foundry Local SDK** - on-device LLM inference (phi-3.5-mini) and embeddings (qwen3-embedding-0.6b)
- **SQLite** - local vector store for document chunks and binary embedding blobs
- **Streamlit** - professional web UI with dark mode, citation badges, and latency metrics
- **Two-layer hallucination guard** - similarity threshold (0.45) + answer quality validation

## Architecture

```
User Query
    |
    v
[Embedding Model]  qwen3-embedding-0.6b (Foundry Local SDK)
    |  Query vector
    v
[SQLite Vector Store]  Cosine similarity search (k=5)
    |  Filtered chunks (score >= 0.45)
    v
[LLM]  phi-3.5-mini (Foundry Local SDK, temperature=0)
    |  Grounded answer + citations
    v
[Streamlit UI]  Answer + latency + source badges
```

## Features

| Feature | Detail |
|---|---|
| Fully Offline | No API keys, no internet after model download |
| GPU Acceleration | WinML / DirectML backend (NVIDIA, AMD, Intel) |
| Hallucination Guard | Dual-layer: similarity threshold + answer length check |
| Source Citations | [Source: filename.md] styled badge rendering |
| Latency Display | End-to-end inference time per query |
| Dynamic Indexing | Drag-and-drop .md / .txt upload, auto re-index |
| Model Switching | Switch LLM via sidebar (phi-3.5-mini / qwen2.5-0.5b) |

## Knowledge Base

| File | Content |
|---|---|
| preflight_checklist.md | Visual inspection, propeller torque, battery voltage (4.2V/cell), IMU calibration |
| failsafe_protocols.md | Low-battery RTL, GPS loss AltHold, RC link loss procedures |
| ardupilot_px4_diagnostics.md | Telemetry codes, compass variance, ESC sync failures, EKF health |
| emergency_procedures.md | Geofence breach, mid-air motor loss, LiPo fire response |
| battery_maintenance.md | Storage voltage, charge cycles, thermal management |

## Installation

```bash
git clone https://github.com/YOUR_USERNAME/uav-drone-rag.git
cd uav-drone-rag
pip install -r requirements.txt
python ingest.py
python -m streamlit run app.py
```

> On first run, Foundry Local SDK downloads the LLM (~2.5 GB) and embedding model (~500 MB). Subsequent runs are fully offline.

## Project Structure

```
uav_drone_rag/
├── app.py              # Streamlit UI
├── rag_engine.py       # RAG pipeline + LLM inference
├── retriever.py        # SQLite vector search + threshold
├── ingest.py           # Document chunking + embedding
├── test_suite.py       # Automated tests
├── requirements.txt
└── data/               # UAV field manuals
```

## Tech Stack

| Component | Technology |
|---|---|
| LLM Inference | Microsoft Foundry Local SDK (phi-3.5-mini) |
| Embeddings | Microsoft Foundry Local SDK (qwen3-embedding-0.6b) |
| Vector Store | SQLite (cosine similarity) |
| UI | Streamlit |
| GPU Backend | WinML / DirectML (foundry-local-sdk-winml) |

## Test Results

```
Test 1 (In-Domain):     "What is the RTL procedure when GPS is lost?" -> PASS
Test 2 (Out-of-Domain): "How do I change oil on a diesel engine?"     -> PASS (refused)
```

## License

MIT License
