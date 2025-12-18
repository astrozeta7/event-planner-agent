import React, { useState } from 'react';
import ChatInterface from './components/ChatInterface';
import EventFormVisualization from './components/EventFormVisualization';
import ResultsDisplay from './components/ResultsDisplay';
import './App.css';

function App() {
  const [eventData, setEventData] = useState({
    event_date: '',
    location: '',
    number_of_guests: null,
    cuisine_preferences: [],
    budget_per_guest: null,
    event_type: '',
    needs_event_room: false,
    special_requirements: ''
  });

  const [results, setResults] = useState(null);
  const [isSearching, setIsSearching] = useState(false);

  return (
    <div className="App">
      <header className="app-header">
        <h1>🎉 Event Planner AI Agent</h1>
        <p>Chat with our AI to plan your perfect event</p>
      </header>

      <div className="app-container">
        <div className="left-panel">
          <ChatInterface 
            eventData={eventData}
            setEventData={setEventData}
            setResults={setResults}
            isSearching={isSearching}
            setIsSearching={setIsSearching}
          />
        </div>

        <div className="right-panel">
          <EventFormVisualization eventData={eventData} />
          {results && <ResultsDisplay results={results} />}
        </div>
      </div>
    </div>
  );
}

export default App;
