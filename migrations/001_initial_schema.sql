-- Initial migration for deal-analysis schema
-- Enable PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;

-- Deals table
CREATE TABLE deals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    deal_value DOUBLE PRECISION,
    deal_type VARCHAR(50),
    status VARCHAR(50) DEFAULT 'active',
    location GEOMETRY(POINT, 4326),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Properties table
CREATE TABLE properties (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    deal_id UUID NOT NULL REFERENCES deals(id) ON DELETE CASCADE,
    address VARCHAR(500),
    city VARCHAR(100),
    state VARCHAR(50),
    country VARCHAR(100),
    postal_code VARCHAR(20),
    boundary GEOMETRY(POLYGON, 4326),
    area_sqft DOUBLE PRECISION,
    bedrooms INTEGER,
    bathrooms DOUBLE PRECISION,
    year_built INTEGER,
    property_type VARCHAR(50),
    estimated_value DOUBLE PRECISION,
    price_per_sqft DOUBLE PRECISION,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Deal analyses table
CREATE TABLE deal_analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    deal_id UUID NOT NULL REFERENCES deals(id) ON DELETE CASCADE,
    analysis_type VARCHAR(100),
    model_version VARCHAR(50),
    score DOUBLE PRECISION,
    summary TEXT,
    details TEXT,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processing_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Pipeline runs table
CREATE TABLE pipeline_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pipeline_name VARCHAR(100) NOT NULL,
    status VARCHAR(50) DEFAULT 'running',
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT,
    records_processed INTEGER DEFAULT 0,
    records_failed INTEGER DEFAULT 0
);

-- Indexes
CREATE INDEX idx_deals_status ON deals(status);
CREATE INDEX idx_deals_location ON deals USING GIST(location);
CREATE INDEX idx_properties_deal_id ON properties(deal_id);
CREATE INDEX idx_properties_boundary ON properties USING GIST(boundary);
CREATE INDEX idx_properties_city_state ON properties(city, state);
CREATE INDEX idx_analysis_deal_id ON deal_analyses(deal_id);
CREATE INDEX idx_analysis_type ON deal_analyses(analysis_type);
CREATE INDEX idx_pipeline_runs_name ON pipeline_runs(pipeline_name);
CREATE INDEX idx_pipeline_runs_status ON pipeline_runs(status);