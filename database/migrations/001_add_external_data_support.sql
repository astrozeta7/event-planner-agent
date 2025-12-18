-- Database Migration: Add External Data Source Support
-- Version: 2.1
-- Created: 2025-12-18
-- Purpose: Add fields to support real-time data from Yelp, Google Maps, and other external sources

-- Add external data fields to venues table
ALTER TABLE venues
ADD COLUMN IF NOT EXISTS external_id VARCHAR(255),
ADD COLUMN IF NOT EXISTS external_source VARCHAR(50) CHECK (external_source IN ('yelp', 'google_maps', 'manual', 'peerspace', 'eventbrite')),
ADD COLUMN IF NOT EXISTS external_url TEXT,
ADD COLUMN IF NOT EXISTS rating DECIMAL(3, 2) CHECK (rating >= 0 AND rating <= 5),
ADD COLUMN IF NOT EXISTS review_count INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS price_level VARCHAR(10),
ADD COLUMN IF NOT EXISTS latitude DECIMAL(10, 8),
ADD COLUMN IF NOT EXISTS longitude DECIMAL(11, 8),
ADD COLUMN IF NOT EXISTS photos JSONB DEFAULT '[]',
ADD COLUMN IF NOT EXISTS business_status VARCHAR(50),
ADD COLUMN IF NOT EXISTS last_synced_at TIMESTAMP WITH TIME ZONE;

-- Add external data fields to caterers table
ALTER TABLE caterers
ADD COLUMN IF NOT EXISTS external_id VARCHAR(255),
ADD COLUMN IF NOT EXISTS external_source VARCHAR(50) CHECK (external_source IN ('yelp', 'google_maps', 'manual', 'thumbtack')),
ADD COLUMN IF NOT EXISTS external_url TEXT,
ADD COLUMN IF NOT EXISTS rating DECIMAL(3, 2) CHECK (rating >= 0 AND rating <= 5),
ADD COLUMN IF NOT EXISTS review_count INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS price_level VARCHAR(10),
ADD COLUMN IF NOT EXISTS latitude DECIMAL(10, 8),
ADD COLUMN IF NOT EXISTS longitude DECIMAL(11, 8),
ADD COLUMN IF NOT EXISTS photos JSONB DEFAULT '[]',
ADD COLUMN IF NOT EXISTS business_status VARCHAR(50),
ADD COLUMN IF NOT EXISTS last_synced_at TIMESTAMP WITH TIME ZONE;

-- Create unique constraint for external IDs
CREATE UNIQUE INDEX IF NOT EXISTS idx_venues_external_id 
ON venues(external_id, external_source) 
WHERE external_id IS NOT NULL;

CREATE UNIQUE INDEX IF NOT EXISTS idx_caterers_external_id 
ON caterers(external_id, external_source) 
WHERE external_id IS NOT NULL;

-- Create indexes for location-based queries
CREATE INDEX IF NOT EXISTS idx_venues_location ON venues(latitude, longitude) WHERE latitude IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_caterers_location ON caterers(latitude, longitude) WHERE latitude IS NOT NULL;

-- Create indexes for rating queries
CREATE INDEX IF NOT EXISTS idx_venues_rating ON venues(rating DESC) WHERE rating IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_caterers_rating ON caterers(rating DESC) WHERE rating IS NOT NULL;

-- Create indexes for external source queries
CREATE INDEX IF NOT EXISTS idx_venues_external_source ON venues(external_source);
CREATE INDEX IF NOT EXISTS idx_caterers_external_source ON caterers(external_source);

-- Create table for storing raw API responses (for debugging and caching)
CREATE TABLE IF NOT EXISTS external_api_cache (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    api_source VARCHAR(50) NOT NULL,
    endpoint VARCHAR(255) NOT NULL,
    request_params JSONB NOT NULL,
    response_data JSONB NOT NULL,
    status_code INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX IF NOT EXISTS idx_api_cache_source ON external_api_cache(api_source);
CREATE INDEX IF NOT EXISTS idx_api_cache_expires ON external_api_cache(expires_at);

-- Create table for tracking data sync jobs
CREATE TABLE IF NOT EXISTS data_sync_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_type VARCHAR(50) NOT NULL CHECK (job_type IN ('venues', 'caterers', 'full_sync')),
    source VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'completed', 'failed')),
    records_processed INTEGER DEFAULT 0,
    records_created INTEGER DEFAULT 0,
    records_updated INTEGER DEFAULT 0,
    records_failed INTEGER DEFAULT 0,
    error_message TEXT,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_sync_jobs_status ON data_sync_jobs(status);
CREATE INDEX IF NOT EXISTS idx_sync_jobs_created ON data_sync_jobs(created_at DESC);

-- Create view for venues with external data
CREATE OR REPLACE VIEW venues_with_external_data AS
SELECT 
    v.*,
    CASE 
        WHEN v.external_source IS NOT NULL THEN true 
        ELSE false 
    END as is_external,
    CASE 
        WHEN v.last_synced_at IS NOT NULL 
        THEN EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - v.last_synced_at)) / 3600 
        ELSE NULL 
    END as hours_since_sync
FROM venues v;

-- Create view for caterers with external data
CREATE OR REPLACE VIEW caterers_with_external_data AS
SELECT 
    c.*,
    CASE 
        WHEN c.external_source IS NOT NULL THEN true 
        ELSE false 
    END as is_external,
    CASE 
        WHEN c.last_synced_at IS NOT NULL 
        THEN EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - c.last_synced_at)) / 3600 
        ELSE NULL 
    END as hours_since_sync
FROM caterers c;

-- Create function to calculate distance between two points (Haversine formula)
CREATE OR REPLACE FUNCTION calculate_distance(
    lat1 DECIMAL, lon1 DECIMAL, 
    lat2 DECIMAL, lon2 DECIMAL
) RETURNS DECIMAL AS $$
DECLARE
    R DECIMAL := 6371;
    dLat DECIMAL;
    dLon DECIMAL;
    a DECIMAL;
    c DECIMAL;
BEGIN
    dLat := radians(lat2 - lat1);
    dLon := radians(lon2 - lon1);
    
    a := sin(dLat/2) * sin(dLat/2) + 
         cos(radians(lat1)) * cos(radians(lat2)) * 
         sin(dLon/2) * sin(dLon/2);
    
    c := 2 * atan2(sqrt(a), sqrt(1-a));
    
    RETURN R * c;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Create function to find nearby venues
CREATE OR REPLACE FUNCTION find_nearby_venues(
    search_lat DECIMAL,
    search_lon DECIMAL,
    radius_km DECIMAL DEFAULT 10
) RETURNS TABLE (
    venue_id UUID,
    venue_name VARCHAR,
    distance_km DECIMAL,
    rating DECIMAL,
    location VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        v.id,
        v.name,
        calculate_distance(search_lat, search_lon, v.latitude, v.longitude) as distance,
        v.rating,
        v.location
    FROM venues v
    WHERE v.latitude IS NOT NULL 
      AND v.longitude IS NOT NULL
      AND v.is_active = true
      AND calculate_distance(search_lat, search_lon, v.latitude, v.longitude) <= radius_km
    ORDER BY distance;
END;
$$ LANGUAGE plpgsql;

-- Create function to find nearby caterers
CREATE OR REPLACE FUNCTION find_nearby_caterers(
    search_lat DECIMAL,
    search_lon DECIMAL,
    radius_km DECIMAL DEFAULT 10
) RETURNS TABLE (
    caterer_id UUID,
    caterer_name VARCHAR,
    distance_km DECIMAL,
    rating DECIMAL,
    location VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        c.id,
        c.name,
        calculate_distance(search_lat, search_lon, c.latitude, c.longitude) as distance,
        c.rating,
        c.location
    FROM caterers c
    WHERE c.latitude IS NOT NULL 
      AND c.longitude IS NOT NULL
      AND c.is_active = true
      AND calculate_distance(search_lat, search_lon, c.latitude, c.longitude) <= radius_km
    ORDER BY distance;
END;
$$ LANGUAGE plpgsql;

-- Add comments for documentation
COMMENT ON COLUMN venues.external_id IS 'Unique identifier from external source (e.g., Yelp business ID)';
COMMENT ON COLUMN venues.external_source IS 'Source of the data (yelp, google_maps, manual, etc.)';
COMMENT ON COLUMN venues.external_url IS 'URL to the external listing';
COMMENT ON COLUMN venues.rating IS 'Average rating from external source (0-5 scale)';
COMMENT ON COLUMN venues.review_count IS 'Number of reviews from external source';
COMMENT ON COLUMN venues.last_synced_at IS 'Last time data was synced from external source';

COMMENT ON COLUMN caterers.external_id IS 'Unique identifier from external source (e.g., Yelp business ID)';
COMMENT ON COLUMN caterers.external_source IS 'Source of the data (yelp, google_maps, manual, etc.)';
COMMENT ON COLUMN caterers.external_url IS 'URL to the external listing';
COMMENT ON COLUMN caterers.rating IS 'Average rating from external source (0-5 scale)';
COMMENT ON COLUMN caterers.review_count IS 'Number of reviews from external source';
COMMENT ON COLUMN caterers.last_synced_at IS 'Last time data was synced from external source';

COMMENT ON TABLE external_api_cache IS 'Cache for external API responses to reduce API calls';
COMMENT ON TABLE data_sync_jobs IS 'Track data synchronization jobs from external sources';
