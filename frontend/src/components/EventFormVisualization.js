import React from 'react';
import { motion } from 'framer-motion';
import { Calendar, MapPin, Users, DollarSign, Utensils, Home, FileText } from 'lucide-react';
import './EventFormVisualization.css';

function EventFormVisualization({ eventData }) {
  const fields = [
    {
      icon: Calendar,
      label: 'Event Date',
      value: eventData.event_date,
      key: 'event_date'
    },
    {
      icon: MapPin,
      label: 'Location',
      value: eventData.location,
      key: 'location'
    },
    {
      icon: Users,
      label: 'Number of Guests',
      value: eventData.number_of_guests,
      key: 'number_of_guests'
    },
    {
      icon: DollarSign,
      label: 'Budget per Guest',
      value: eventData.budget_per_guest ? `$${eventData.budget_per_guest}` : null,
      key: 'budget_per_guest'
    },
    {
      icon: Utensils,
      label: 'Cuisine Preferences',
      value: eventData.cuisine_preferences?.length > 0 
        ? eventData.cuisine_preferences.join(', ') 
        : null,
      key: 'cuisine_preferences'
    },
    {
      icon: Home,
      label: 'Event Type',
      value: eventData.event_type,
      key: 'event_type'
    },
    {
      icon: Home,
      label: 'Needs Event Room',
      value: eventData.needs_event_room ? 'Yes' : 'No',
      key: 'needs_event_room',
      alwaysShow: true
    },
    {
      icon: FileText,
      label: 'Special Requirements',
      value: eventData.special_requirements,
      key: 'special_requirements'
    }
  ];

  const filledFields = fields.filter(f => f.value || f.alwaysShow).length;
  const totalFields = fields.length;
  const progress = (filledFields / totalFields) * 100;

  return (
    <div className="form-visualization">
      <div className="form-header">
        <h2>Event Details</h2>
        <div className="progress-container">
          <div className="progress-bar">
            <motion.div 
              className="progress-fill"
              initial={{ width: 0 }}
              animate={{ width: `${progress}%` }}
              transition={{ duration: 0.5 }}
            />
          </div>
          <span className="progress-text">{filledFields}/{totalFields} fields</span>
        </div>
      </div>

      <div className="form-fields">
        {fields.map((field) => {
          const Icon = field.icon;
          const isFilled = field.value || field.alwaysShow;
          
          return (
            <motion.div
              key={field.key}
              className={`form-field ${isFilled ? 'filled' : 'empty'}`}
              initial={{ opacity: 0.5, scale: 0.95 }}
              animate={{ 
                opacity: isFilled ? 1 : 0.5,
                scale: isFilled ? 1 : 0.95
              }}
              transition={{ duration: 0.3 }}
            >
              <div className="field-icon">
                <Icon size={20} />
              </div>
              <div className="field-content">
                <div className="field-label">{field.label}</div>
                <div className="field-value">
                  {field.value || <span className="placeholder">Not specified yet</span>}
                </div>
              </div>
              {isFilled && (
                <motion.div
                  className="check-mark"
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ type: 'spring', stiffness: 500, damping: 30 }}
                >
                  ✓
                </motion.div>
              )}
            </motion.div>
          );
        })}
      </div>

      {progress === 100 && (
        <motion.div
          className="completion-badge"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          🎉 All details collected! Ready to search!
        </motion.div>
      )}
    </div>
  );
}

export default EventFormVisualization;
