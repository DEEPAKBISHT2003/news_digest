-- schema.sql
-- Production-grade news intelligence schema

CREATE TABLE IF NOT EXISTS news_articles (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    summary TEXT,
    content TEXT,
    source TEXT,
    url TEXT UNIQUE NOT NULL,
    published_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Domain Classification
    dominant_category TEXT,
    domain_percentages JSONB, -- { "AI": 0.8, "Finance": 0.2 }
    
    -- Scores
    importance_score FLOAT DEFAULT 0,
    trend_score FLOAT DEFAULT 0,
    fact_score FLOAT DEFAULT 0,
    confidence_score FLOAT DEFAULT 0,
    
    -- Status
    dedup_status BOOLEAN DEFAULT FALSE,
    is_processed BOOLEAN DEFAULT FALSE,
    
    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,
    structured_data JSONB DEFAULT '{}'::jsonb -- Stores Quick Take, Key Points, etc.
);

CREATE INDEX IF NOT EXISTS idx_news_articles_url ON news_articles(url);
CREATE INDEX IF NOT EXISTS idx_news_articles_published_at ON news_articles(published_at);
CREATE INDEX IF NOT EXISTS idx_news_articles_dominant_category ON news_articles(dominant_category);
