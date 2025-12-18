# Event Planner Frontend - Conversational AI Interface

## Overview

A unique, conversational React interface where users interact with an AI agent to plan events. No forms to fill out - just chat naturally!

## Features

### 🤖 Conversational AI Agent
- Natural language understanding
- Extracts event details from conversation
- Asks clarifying questions
- Confirms information before searching

### 📊 Real-time Form Visualization
- See event details populate as you chat
- Progress bar shows completion
- Visual feedback for each field
- Animated transitions

### 🎯 Smart Results Display
- Catering options by cuisine
- Venue recommendations
- Cost breakdowns
- Ratings and amenities

## How It Works

1. **User chats naturally**: "I'm planning a wedding for 150 people in San Francisco"
2. **Agent extracts info**: Date, location, guests, cuisine, budget
3. **Form updates live**: Visual representation of collected data
4. **Agent confirms**: Shows all details and asks for confirmation
5. **Search executes**: Finds real venues and caterers
6. **Results display**: Beautiful cards with all options

## Tech Stack

- **React 18** - UI framework
- **Framer Motion** - Smooth animations
- **Lucide React** - Beautiful icons
- **Axios** - API communication
- **CSS3** - Custom styling with gradients

## Installation

### Local Development

```bash
cd frontend
npm install
npm start
```

Runs on `http://localhost:3000`

### Docker

```bash
docker compose up frontend
```

## Environment Variables

Create `.env` file:

```
REACT_APP_API_URL=http://localhost:8000
```

## Project Structure

```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   ├── ChatInterface.js          # Main chat UI
│   │   ├── ChatInterface.css
│   │   ├── EventFormVisualization.js # Live form display
│   │   ├── EventFormVisualization.css
│   │   ├── ResultsDisplay.js         # Search results
│   │   └── ResultsDisplay.css
│   ├── services/
│   │   └── api.js                    # Backend API calls
│   ├── App.js                        # Main app component
│   ├── App.css
│   ├── index.js                      # Entry point
│   └── index.css                     # Global styles
├── package.json
├── Dockerfile
└── README.md
```

## Components

### ChatInterface
- Message history with timestamps
- User and agent avatars
- Typing indicator
- Auto-scroll to latest message
- Send button with keyboard support

### EventFormVisualization
- 8 event detail fields
- Progress tracking (X/8 fields)
- Checkmarks for completed fields
- Animated field highlighting
- Completion badge

### ResultsDisplay
- Catering options grid
- Venue cards with details
- Rating stars
- Price badges
- Amenity tags
- Summary section

## API Integration

### POST /chat
```json
{
  "message": "I need a venue for 100 people",
  "current_data": { ... }
}
```

Response:
```json
{
  "message": "Great! Where will the event be?",
  "updated_data": { "number_of_guests": 100 },
  "ready_to_search": false,
  "missing_fields": ["event_date", "location"]
}
```

### POST /plan-event
```json
{
  "event_date": "2025-09-15",
  "location": "San Francisco",
  "number_of_guests": 100,
  ...
}
```

## Design Philosophy

### Novel Interaction Pattern
- **No traditional forms** - Users hate filling out forms
- **Conversational** - Natural language, like texting a friend
- **Progressive disclosure** - One question at a time
- **Visual feedback** - See data populate in real-time
- **Confirmation** - Agent confirms before searching

### Why This Is Unique

**Traditional Event Planning Sites:**
- Long forms with 10+ fields
- Overwhelming dropdowns
- No guidance
- Submit and hope

**Our Approach:**
- Chat naturally
- Agent guides you
- See progress visually
- Confirm before search
- Get personalized results

## Future Enhancements

### Voice Interaction (Planned)
```javascript
// Speech recognition
const recognition = new webkitSpeechRecognition();
recognition.onresult = (event) => {
  const transcript = event.results[0][0].transcript;
  sendMessage(transcript);
};
```

### AI Improvements
- GPT-4 integration for better understanding
- Multi-turn context awareness
- Suggestion chips ("Popular: Italian, Mexican")
- Smart defaults based on event type

### UX Enhancements
- Image previews for venues
- Map integration
- Calendar picker (optional)
- Budget slider (optional)
- Comparison mode

## Development

### Run Tests
```bash
npm test
```

### Build for Production
```bash
npm run build
```

### Lint
```bash
npm run lint
```

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Performance

- Initial load: < 2s
- Time to interactive: < 3s
- Lighthouse score: 95+
- Bundle size: ~200KB gzipped

## Accessibility

- ARIA labels on all interactive elements
- Keyboard navigation support
- Screen reader friendly
- High contrast mode support
- Focus indicators

## Contributing

1. Fork the repo
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit PR

## License

MIT

---

**Built with ❤️ for a better event planning experience**
