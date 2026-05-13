# System Execution Flow

```mermaid
graph TD
    Trigger[Cron Trigger / Manual] --> Orchestrator[System Orchestrator]
    
    subgraph Parallel Domains
        AI[AI Pipeline]
        Finance[Finance Pipeline]
        Sports[Sports Pipeline]
        Politics[Politics Pipeline]
        Incidents[Incidents Pipeline]
    end

    Orchestrator --> AI
    Orchestrator --> Finance
    Orchestrator --> Sports
    Orchestrator --> Politics
    Orchestrator --> Incidents

    subgraph Per-Domain Pipeline
        Ingest[Hybrid Ingestion: RSS + Tavily] --> Classify[Domain Classifier & Scoring]
        Classify --> DB[(PostgreSQL)]
        DB --> Dedup[Deduplication Agent]
        Dedup --> Graph[LangGraph Workflow]
    end

    AI --> Ingest
    
    subgraph LangGraph Intelligence Loop
        Writer[Writer Agent] --> Eval[Evaluator Agent]
        Eval -- Invalid --> Correct[Corrector Agent]
        Correct --> Eval
        Eval -- Valid --> Output[Final Digest]
    end

    Graph --> Writer
    Output --> PDF[PDF Export]
    Output --> JSON[App JSON Store]
```

## Step-by-Step
1. **Trigger**: System starts via `production_main.py` or Cron.
2. **Parallel Fan-out**: Orchestrator spawns tasks for each domain (AI, Finance, etc.).
3. **Ingestion**: For each domain, it fetches from RSS feeds and Tavily Search.
4. **Processing**: Articles are classified by percentage (e.g., 90% AI, 10% Finance) and scored for importance.
5. **Persistence**: Data is saved to PostgreSQL with a deduplication check.
6. **Intelligence**: LangGraph is triggered for each domain to generate a high-quality digest.
7. **Correction**: Evaluator checks for hallucinations; Corrector fixes them.
8. **Finalization**: Digests are exported to PDF and ready for API consumption.
