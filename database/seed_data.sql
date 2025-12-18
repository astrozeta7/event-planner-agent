-- Seed data migration script
-- Migrates mock data from V1 to PostgreSQL

-- Insert mock venues
INSERT INTO venues (name, location, address, capacity_min, capacity_max, base_room_rental_fee, hourly_rate, includes_catering, supported_cuisines_if_included, amenities, description) VALUES
('Bayview Ballroom', 'San Francisco', '123 Bay Street, San Francisco, CA 94133', 50, 200, 3000.00, 200.00, FALSE, NULL, ARRAY['AV equipment', 'Stage', 'Parking', 'WiFi', 'Dance floor'], 'Elegant ballroom with stunning bay views'),
('Golden Gate Conference Center', 'San Francisco', '456 Golden Gate Ave, San Francisco, CA 94102', 100, 500, 5000.00, 300.00, TRUE, ARRAY['American', 'Italian', 'Asian Fusion'], ARRAY['AV equipment', 'Stage', 'Parking', 'WiFi', 'Catering kitchen', 'Green room'], 'Premier conference center with full catering services'),
('Marina View Loft', 'San Francisco', '789 Marina Blvd, San Francisco, CA 94123', 30, 120, 2000.00, 150.00, FALSE, NULL, ARRAY['WiFi', 'Parking', 'Rooftop access', 'City views'], 'Modern loft space with panoramic city views'),
('Manhattan Grand Hall', 'New York', '100 Broadway, New York, NY 10005', 150, 600, 8000.00, 500.00, TRUE, ARRAY['Italian', 'French', 'American', 'Fusion'], ARRAY['AV equipment', 'Stage', 'Valet parking', 'WiFi', 'Crystal chandeliers', 'Bridal suite'], 'Luxurious grand hall in the heart of Manhattan'),
('Brooklyn Warehouse Space', 'New York', '200 Kent Ave, Brooklyn, NY 11249', 50, 250, 3500.00, 250.00, FALSE, NULL, ARRAY['WiFi', 'Parking', 'Industrial aesthetic', 'Flexible layout'], 'Trendy warehouse space in Williamsburg'),
('Hollywood Hills Estate', 'Los Angeles', '300 Hollywood Hills Dr, Los Angeles, CA 90068', 80, 300, 6000.00, 400.00, FALSE, NULL, ARRAY['Pool area', 'Garden', 'Parking', 'WiFi', 'Outdoor kitchen', 'Sunset views'], 'Stunning estate with Hollywood Hills views'),
('Santa Monica Beach Club', 'Los Angeles', '400 Ocean Ave, Santa Monica, CA 90401', 40, 180, 4000.00, 300.00, TRUE, ARRAY['Mexican', 'American', 'Seafood'], ARRAY['Beach access', 'Parking', 'WiFi', 'Outdoor seating', 'Fire pits'], 'Beachfront venue with ocean views'),
('Chicago Skyline Tower', 'Chicago', '500 Michigan Ave, Chicago, IL 60611', 100, 400, 5500.00, 350.00, FALSE, NULL, ARRAY['AV equipment', 'Parking', 'WiFi', 'Panoramic views', 'Multiple rooms'], 'High-rise venue with stunning skyline views'),
('Austin Music Hall', 'Austin', '600 Congress Ave, Austin, TX 78701', 60, 250, 3000.00, 200.00, FALSE, NULL, ARRAY['Stage', 'Sound system', 'Parking', 'WiFi', 'Bar area', 'Green room'], 'Live music venue in downtown Austin'),
('Hill Country Ranch Venue', 'Austin', '700 Ranch Rd, Austin, TX 78737', 50, 300, 4500.00, 250.00, TRUE, ARRAY['American', 'BBQ', 'Mexican'], ARRAY['Outdoor space', 'Parking', 'WiFi', 'Rustic barn', 'Fire pit', 'Lawn games'], 'Rustic ranch venue in the Texas Hill Country');

-- Insert mock caterers
INSERT INTO caterers (name, location, address, supported_cuisines, base_price_per_guest, service_fee_flat, tax_rate_percent, min_guests, max_guests, notes) VALUES
('La Bella Catering', 'San Francisco', '111 Italian Way, San Francisco, CA 94110', ARRAY['Italian'], 75.00, 500.00, 9.5, 30, 250, 'Halal-friendly options available, family recipes from Tuscany'),
('Spice Route Catering', 'San Francisco', '222 Curry Lane, San Francisco, CA 94103', ARRAY['Indian'], 65.00, 400.00, 9.5, 25, 300, 'Authentic North and South Indian cuisine, vegan options available'),
('Global Fusion Events', 'San Francisco', '333 Fusion St, San Francisco, CA 94107', ARRAY['Italian', 'Indian', 'Fusion', 'Mediterranean'], 85.00, 600.00, 9.5, 50, 200, 'Award-winning fusion cuisine, customizable menus'),
('Mama Rosa''s Catering', 'New York', '444 Little Italy, New York, NY 10013', ARRAY['Italian', 'American'], 70.00, 450.00, 8.875, 40, 300, 'Traditional Italian-American cuisine, gluten-free options'),
('Golden Dragon Catering', 'San Francisco', '555 Chinatown, San Francisco, CA 94108', ARRAY['Chinese', 'Asian Fusion'], 60.00, 350.00, 9.5, 30, 400, 'Dim sum specialists, nut-free options available'),
('Fiesta Catering Co', 'Los Angeles', '666 Olvera St, Los Angeles, CA 90012', ARRAY['Mexican', 'Latin American'], 55.00, 300.00, 9.5, 20, 500, 'Authentic Mexican cuisine, taco bars, vegetarian-friendly'),
('Sakura Catering Services', 'Los Angeles', '777 Little Tokyo, Los Angeles, CA 90012', ARRAY['Japanese', 'Asian Fusion'], 90.00, 700.00, 9.5, 30, 150, 'Sushi and hibachi specialists, premium ingredients'),
('All-American Catering', 'Chicago', '888 State St, Chicago, IL 60605', ARRAY['American', 'BBQ'], 65.00, 400.00, 10.25, 50, 500, 'BBQ, comfort food, farm-to-table options'),
('Taj Mahal Catering', 'New York', '999 Curry Hill, New York, NY 10016', ARRAY['Indian', 'Pakistani'], 68.00, 420.00, 8.875, 35, 250, 'Halal certified, extensive vegetarian menu'),
('Mediterranean Delights', 'Austin', '1010 Med Way, Austin, TX 78701', ARRAY['Mediterranean', 'Greek', 'Middle Eastern'], 72.00, 450.00, 8.25, 30, 200, 'Fresh ingredients, vegan and gluten-free options');

-- Verify data
SELECT 'Venues inserted: ' || COUNT(*) FROM venues;
SELECT 'Caterers inserted: ' || COUNT(*) FROM caterers;
