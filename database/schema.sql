-- Event Planner Database Schema
-- Version: 1.0
-- Created: 2025-12-18

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    phone VARCHAR(50),
    company_name VARCHAR(255),
    user_type VARCHAR(50) NOT NULL CHECK (user_type IN ('client', 'venue_manager', 'caterer', 'admin')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Venues table
CREATE TABLE venues (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    location VARCHAR(255) NOT NULL,
    address TEXT,
    capacity_min INTEGER NOT NULL CHECK (capacity_min > 0),
    capacity_max INTEGER NOT NULL CHECK (capacity_max >= capacity_min),
    base_room_rental_fee DECIMAL(10, 2) NOT NULL CHECK (base_room_rental_fee >= 0),
    hourly_rate DECIMAL(10, 2) CHECK (hourly_rate >= 0),
    includes_catering BOOLEAN DEFAULT FALSE,
    supported_cuisines_if_included TEXT[],
    amenities TEXT[] DEFAULT '{}',
    description TEXT,
    contact_email VARCHAR(255),
    contact_phone VARCHAR(50),
    manager_id UUID REFERENCES users(id),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Caterers table
CREATE TABLE caterers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    location VARCHAR(255) NOT NULL,
    address TEXT,
    supported_cuisines TEXT[] NOT NULL,
    base_price_per_guest DECIMAL(10, 2) NOT NULL CHECK (base_price_per_guest >= 0),
    service_fee_flat DECIMAL(10, 2) NOT NULL CHECK (service_fee_flat >= 0),
    tax_rate_percent DECIMAL(5, 2) NOT NULL CHECK (tax_rate_percent >= 0 AND tax_rate_percent <= 100),
    min_guests INTEGER NOT NULL CHECK (min_guests > 0),
    max_guests INTEGER NOT NULL CHECK (max_guests >= min_guests),
    notes TEXT,
    contact_email VARCHAR(255),
    contact_phone VARCHAR(50),
    manager_id UUID REFERENCES users(id),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Bookings table
CREATE TABLE bookings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    booking_reference VARCHAR(50) UNIQUE NOT NULL,
    client_id UUID NOT NULL REFERENCES users(id),
    venue_id UUID REFERENCES venues(id),
    caterer_id UUID REFERENCES caterers(id),
    event_date DATE NOT NULL,
    event_start_time TIME,
    event_end_time TIME,
    number_of_guests INTEGER NOT NULL CHECK (number_of_guests > 0),
    event_type VARCHAR(100),
    cuisine_preferences TEXT[],
    special_requirements TEXT,
    status VARCHAR(50) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'confirmed', 'cancelled', 'completed')),
    venue_cost DECIMAL(10, 2),
    catering_cost DECIMAL(10, 2),
    total_cost DECIMAL(10, 2),
    deposit_paid DECIMAL(10, 2) DEFAULT 0,
    balance_due DECIMAL(10, 2),
    payment_status VARCHAR(50) DEFAULT 'unpaid' CHECK (payment_status IN ('unpaid', 'deposit_paid', 'paid', 'refunded')),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Venue availability calendar
CREATE TABLE venue_availability (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    venue_id UUID NOT NULL REFERENCES venues(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    is_available BOOLEAN DEFAULT TRUE,
    booking_id UUID REFERENCES bookings(id) ON DELETE SET NULL,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(venue_id, date)
);

-- Caterer availability calendar
CREATE TABLE caterer_availability (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    caterer_id UUID NOT NULL REFERENCES caterers(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    is_available BOOLEAN DEFAULT TRUE,
    booking_id UUID REFERENCES bookings(id) ON DELETE SET NULL,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(caterer_id, date)
);

-- Documents table (for Google Drive integration)
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    booking_id UUID REFERENCES bookings(id) ON DELETE CASCADE,
    venue_id UUID REFERENCES venues(id) ON DELETE CASCADE,
    caterer_id UUID REFERENCES caterers(id) ON DELETE CASCADE,
    document_type VARCHAR(100) NOT NULL CHECK (document_type IN ('contract', 'menu', 'floor_plan', 'invoice', 'receipt', 'other')),
    document_name VARCHAR(255) NOT NULL,
    google_drive_file_id VARCHAR(255),
    google_drive_url TEXT,
    file_size_bytes BIGINT,
    mime_type VARCHAR(100),
    uploaded_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Reviews table
CREATE TABLE reviews (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    booking_id UUID NOT NULL REFERENCES bookings(id) ON DELETE CASCADE,
    reviewer_id UUID NOT NULL REFERENCES users(id),
    venue_id UUID REFERENCES venues(id),
    caterer_id UUID REFERENCES caterers(id),
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    review_text TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Pricing history (for analytics and dynamic pricing)
CREATE TABLE pricing_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    venue_id UUID REFERENCES venues(id) ON DELETE CASCADE,
    caterer_id UUID REFERENCES caterers(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    base_price DECIMAL(10, 2) NOT NULL,
    demand_multiplier DECIMAL(5, 2) DEFAULT 1.0,
    final_price DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_venues_location ON venues(location);
CREATE INDEX idx_venues_capacity ON venues(capacity_min, capacity_max);
CREATE INDEX idx_venues_active ON venues(is_active);

CREATE INDEX idx_caterers_location ON caterers(location);
CREATE INDEX idx_caterers_capacity ON caterers(min_guests, max_guests);
CREATE INDEX idx_caterers_active ON caterers(is_active);
CREATE INDEX idx_caterers_cuisines ON caterers USING GIN(supported_cuisines);

CREATE INDEX idx_bookings_client ON bookings(client_id);
CREATE INDEX idx_bookings_venue ON bookings(venue_id);
CREATE INDEX idx_bookings_caterer ON bookings(caterer_id);
CREATE INDEX idx_bookings_date ON bookings(event_date);
CREATE INDEX idx_bookings_status ON bookings(status);
CREATE INDEX idx_bookings_reference ON bookings(booking_reference);

CREATE INDEX idx_venue_availability_date ON venue_availability(venue_id, date);
CREATE INDEX idx_caterer_availability_date ON caterer_availability(caterer_id, date);

CREATE INDEX idx_documents_booking ON documents(booking_id);
CREATE INDEX idx_documents_type ON documents(document_type);

CREATE INDEX idx_reviews_venue ON reviews(venue_id);
CREATE INDEX idx_reviews_caterer ON reviews(caterer_id);

-- Triggers for updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_venues_updated_at BEFORE UPDATE ON venues
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_caterers_updated_at BEFORE UPDATE ON caterers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_bookings_updated_at BEFORE UPDATE ON bookings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to generate booking reference
CREATE OR REPLACE FUNCTION generate_booking_reference()
RETURNS TRIGGER AS $$
BEGIN
    NEW.booking_reference = 'BK-' || TO_CHAR(NEW.created_at, 'YYYYMMDD') || '-' || LPAD(NEXTVAL('booking_ref_seq')::TEXT, 6, '0');
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE SEQUENCE booking_ref_seq START 1;

CREATE TRIGGER set_booking_reference BEFORE INSERT ON bookings
    FOR EACH ROW EXECUTE FUNCTION generate_booking_reference();

-- Views for common queries
CREATE VIEW active_venues AS
SELECT 
    v.*,
    COUNT(DISTINCT b.id) as total_bookings,
    AVG(r.rating) as average_rating
FROM venues v
LEFT JOIN bookings b ON v.id = b.venue_id
LEFT JOIN reviews r ON v.id = r.venue_id
WHERE v.is_active = TRUE
GROUP BY v.id;

CREATE VIEW active_caterers AS
SELECT 
    c.*,
    COUNT(DISTINCT b.id) as total_bookings,
    AVG(r.rating) as average_rating
FROM caterers c
LEFT JOIN bookings b ON c.id = b.caterer_id
LEFT JOIN reviews r ON c.id = r.caterer_id
WHERE c.is_active = TRUE
GROUP BY c.id;

CREATE VIEW upcoming_bookings AS
SELECT 
    b.*,
    u.full_name as client_name,
    u.email as client_email,
    v.name as venue_name,
    c.name as caterer_name
FROM bookings b
JOIN users u ON b.client_id = u.id
LEFT JOIN venues v ON b.venue_id = v.id
LEFT JOIN caterers c ON b.caterer_id = c.id
WHERE b.event_date >= CURRENT_DATE
AND b.status IN ('pending', 'confirmed')
ORDER BY b.event_date;
