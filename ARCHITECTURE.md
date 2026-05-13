# AI News Intelligence Platform - Architecture

## High-Level Overview
A production-grade, autonomous multi-agent platform for intelligence gathering, classification, deduplication, and digest generation.

## Key Layers

### 1. Orchestration Layer
- **SystemOrchestrator**: Manages parallel domain execution and cron scheduling (APScheduler).
- **Fault Tolerance**: Isolated failure handling for each domain.

### 2. Ingestion Layer
- **Hybrid Source Ingestion**: Combines Tavily Search API with domain-specific RSS feeds.
- **Parallel Fetching**: Uses `asyncio` to gather data across multiple sources simultaneously.

### 3. Processing Layer
- **Domain Classification**: Multi-domain percentage scoring (e.g., AI: 80%, Finance: 20%).
- **Scoring Engine**: Evaluates Importance, Trend, and Factuality.
- **Deduplication**: Semantic and URL-based filtering to ensure unique insights.

### 4. Intelligence Graph (LangGraph)
- **State-Driven Workflow**: Orchestrates writers, evaluators, and correctors.
- **Self-Correction Loop**: Evaluator detects issues; Corrector refines output.

### 5. Persistence Layer
- **PostgreSQL**: Centralized storage for articles, metadata, and scores.
- **Repository Pattern**: Clean abstraction for DB operations.

### 6. Output Layer
- **PDF Generation**: High-fidelity digests with analytical insights.
- **API-Ready JSON**: Structured data for downstream application consumption.

## Component Map
- `agents/`: Domain-specific and core agents.
- `db/`: Database schema and connection logic.
- `classification/`: Domain scoring and classification engines.
- `orchestrator/`: Global pipeline management.
- `pipelines/`: Data ingestion logic.
- `graph/`: LangGraph workflow definition.
