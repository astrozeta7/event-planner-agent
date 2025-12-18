import React from 'react';
import { motion } from 'framer-motion';
import { MapPin, DollarSign, Users, Star, Phone, Globe } from 'lucide-react';
import './ResultsDisplay.css';

function ResultsDisplay({ results }) {
  if (!results) return null;

  return (
    <div className="results-display">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <h2 className="results-title">🎯 Search Results</h2>

        {results.catering_analysis?.by_cuisine && results.catering_analysis.by_cuisine.length > 0 && (
          <div className="results-section">
            <h3>🍽️ Catering Options</h3>
            <div className="results-grid">
              {results.catering_analysis.by_cuisine.map((cuisine, index) => (
                <motion.div
                  key={index}
                  className="result-card"
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: index * 0.1 }}
                >
                  <div className="card-header">
                    <h4>{cuisine.cuisine}</h4>
                    <div className="price-badge">
                      <DollarSign size={16} />
                      ${cuisine.avg_cost_per_guest}/guest
                    </div>
                  </div>
                  <div className="card-body">
                    <div className="info-row">
                      <Users size={16} />
                      <span>{cuisine.caterer_count} caterers available</span>
                    </div>
                    <div className="info-row">
                      <DollarSign size={16} />
                      <span>Total: ${cuisine.total_cost}</span>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        )}

        {results.event_rooms && results.event_rooms.length > 0 && (
          <div className="results-section">
            <h3>🏛️ Event Venues</h3>
            <div className="results-grid">
              {results.event_rooms.map((venue, index) => (
                <motion.div
                  key={index}
                  className="result-card venue-card"
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: index * 0.1 }}
                >
                  <div className="card-header">
                    <h4>{venue.name}</h4>
                    {venue.rating && (
                      <div className="rating">
                        <Star size={16} fill="#fbbf24" color="#fbbf24" />
                        <span>{venue.rating}</span>
                      </div>
                    )}
                  </div>
                  <div className="card-body">
                    <div className="info-row">
                      <MapPin size={16} />
                      <span>{venue.location}</span>
                    </div>
                    <div className="info-row">
                      <Users size={16} />
                      <span>Capacity: {venue.capacity} guests</span>
                    </div>
                    <div className="info-row">
                      <DollarSign size={16} />
                      <span>${venue.hourly_rate}/hour</span>
                    </div>
                    {venue.amenities && venue.amenities.length > 0 && (
                      <div className="amenities">
                        {venue.amenities.slice(0, 3).map((amenity, i) => (
                          <span key={i} className="amenity-tag">{amenity}</span>
                        ))}
                      </div>
                    )}
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        )}

        {results.summary_text && (
          <motion.div
            className="summary-section"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
          >
            <h3>📊 Summary</h3>
            <p>{results.summary_text}</p>
          </motion.div>
        )}
      </motion.div>
    </div>
  );
}

export default ResultsDisplay;
