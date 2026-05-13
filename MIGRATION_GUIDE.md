# Migration Guide: Legacy to Production

## Summary of Changes
1. **Parallel Execution**: Domains now run in parallel instead of one-by-one based on a single query.
2. **PostgreSQL**: Replaced local memory/temp storage with persistent PostgreSQL.
3. **Cron Support**: Added APScheduler for automated 2-hour runs.
4. **Hybrid Ingestion**: Integrated RSS feeds alongside Tavily search.
5. **Class-based Agents**: Refactored core agents into classes for better reliability.

## Steps to Migrate

### 1. Environment Variables
Add the following to your `.env` file:
```env
POSTGRES_URL=postgresql://user:password@localhost:5432/news_db
RUN_ON_STARTUP=true
```

### 2. Database Setup
Run the SQL schema provided in `db/schema.sql` on your PostgreSQL instance.

### 3. Dependencies
Install the updated requirements:
```bash
pip install -r requirements.txt
```

### 4. Running the System
Instead of `python main.py` (which still works for single queries), use:
```bash
python production_main.py
```

## Backward Compatibility
- `main.py` is still available for manual testing.
- Agent domain structure remains intact in `agents/`.
- `workflow.py` has been updated but retains the core node-based logic.
