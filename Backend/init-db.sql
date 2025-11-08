-- PostgreSQL initialization script for Growgent
-- This script runs automatically when the PostgreSQL container is first created

-- Enable PostGIS extension for spatial queries
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;

-- Create database if it doesn't exist (handled by POSTGRES_DB env var)
-- But we can add additional setup here

-- Grant permissions (if needed for multi-user setup)
-- GRANT ALL PRIVILEGES ON DATABASE growgent TO postgres;

-- Log successful initialization
DO $$
BEGIN
    RAISE NOTICE 'Growgent database initialized with PostGIS extension';
END $$;


