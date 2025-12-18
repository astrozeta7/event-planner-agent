# 🎉 Conversational Event Planner - Quick Start Guide

## What's New in V2.1?

### ✨ **Conversational AI Interface**
No more boring forms! Just chat naturally with our AI agent to plan your event.

### 🎯 **How It Works**

1. **You**: "I'm planning a wedding for 150 people in San Francisco on September 15th"
2. **AI Agent**: Extracts → Date: 2025-09-15, Location: San Francisco, Guests: 150
3. **Form Updates**: See fields populate in real-time on the right side
4. **AI Agent**: "Great! What's your budget per guest?"
5. **You**: "$100 per person, Italian food"
6. **AI Agent**: Confirms all details and searches
7. **Results**: Real venues and caterers appear!

---

## 🚀 Quick Start (3 Steps)

### Step 1: Start the Backend
```bash
docker compose up -d postgres redis mcp-scraper mcp-geocoding api
```

Wait 30 seconds for services to start.

### Step 2: Start the Frontend
```bash
cd frontend
npm install
npm start
```

Frontend runs on `http://localhost:3000`

### Step 3: Chat with the Agent!
Open browser → `http://localhost:3000` → Start chatting!

---

## 💬 Example Conversations

### Example 1: Wedding
```
You: Hi! I'm planning a wedding
Agent: Great! When is your wedding?
You: September 15, 2025 in San Francisco
Agent: Perfect! How many guests?
You: 150 people
Agent: What's your budget per guest?
You: $100 per person
Agent: Any cuisine preferences?
You: Italian food
Agent: Do you need a venue?
You: Yes
Agent: [Shows all details] Ready to search!
```

### Example 2: Corporate Event
```
You: I need to plan a corporate event for 50 people in New York on December 10th. Budget is $80 per person. Need a venue with AV equipment.
Agent: [Extracts everything] Perfect! Let me search for you...
```

### Example 3: Birthday Party
```
You: Birthday party, 30 guests, Austin Texas, next month
Agent: Great! What date next month?
You: March 20th
Agent: Budget per guest?
You: $50
Agent: Cuisine preferences?
You: Mexican food
Agent: Need a venue?
You: No, I have one
Agent: [Searches for caterers only]
```

---

## 🎨 UI Features

### Chat Interface (Left Side)
- 🤖 AI agent avatar
- 👤 Your avatar
- ⏰ Timestamps
- 💬 Smooth animations
- ⌨️ Press Enter to send

### Form Visualization (Right Side)
- 📊 Progress bar (X/8 fields)
- ✅ Checkmarks for completed fields
- 🎯 Real-time updates
- 🎉 Completion badge

### Results Display (Bottom Right)
- 🍽️ Catering options by cuisine
- 🏛️ Venue cards with details
- ⭐ Ratings
- 💰 Pricing
- 📍 Locations

---

## 🧠 What the Agent Understands

### Dates
- "September 15, 2025"
- "2025-09-15"
- "9/15/2025"
- "next month"

### Locations
- "San Francisco"
- "New York"
- "in Austin"
- "near Chicago"

### Guest Count
- "150 people"
- "50 guests"
- "for 100"
- "about 75 attendees"

### Budget
- "$100 per person"
- "budget is $80 per guest"
- "$50 per head"

### Cuisines
- Italian, Chinese, Japanese, Mexican, Indian
- Thai, French, Mediterranean, American
- Greek, Spanish, Korean, Vietnamese

### Event Types
- Wedding, Corporate, Birthday, Anniversary
- Graduation, Baby Shower, Holiday, Fundraiser

### Special Requirements
- "vegetarian options"
- "gluten-free"
- "nut-free"
- "kosher"

---

## 🛠️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                   React Frontend                     │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │
│  │     Chat     │  │     Form     │  │  Results  │ │
│  │  Interface   │  │Visualization │  │  Display  │ │
│  └──────────────┘  └──────────────┘  └───────────┘ │
└─────────────────────────────────────────────────────┘
                         ↓ HTTP
┌─────────────────────────────────────────────────────┐
│                  FastAPI Backend                     │
│  ┌──────────────────────────────────────────────┐  │
│  │        Conversational Agent Service          │  │
│  │  • NLP extraction (regex-based)              │  │
│  │  • Missing field detection                   │  │
│  │  • Response generation                       │  │
│  └──────────────────────────────────────────────┘  │
│                         ↓                            │
│  ┌──────────────────────────────────────────────┐  │
│  │         Event Planning Service               │  │
│  │  • Search caterers                           │  │
│  │  • Search venues                             │  │
│  │  • Calculate costs                           │  │
│  └──────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────┐
│              MCP Servers (Free APIs)                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐ │
│  │   OSM    │  │Nominatim │  │     Photon       │ │
│  │ Scraper  │  │Geocoding │  │  Place Search    │ │
│  └──────────┘  └──────────┘  └──────────────────┘ │
└─────────────────────────────────────────────────────┘
```

---

## 📝 API Endpoints

### POST /chat
Conversational interaction with the agent.

**Request:**
```json
{
  "message": "I need a venue for 100 people",
  "current_data": {
    "event_date": "",
    "location": "",
    "number_of_guests": null
  }
}
```

**Response:**
```json
{
  "message": "Great! Where will the event be?",
  "updated_data": {
    "event_date": "",
    "location": "",
    "number_of_guests": 100
  },
  "ready_to_search": false,
  "missing_fields": ["event_date", "location"]
}
```

### POST /plan-event
Execute the event search.

**Request:**
```json
{
  "event_date": "2025-09-15",
  "location": "San Francisco",
  "number_of_guests": 150,
  "cuisine_preferences": ["Italian"],
  "budget_per_guest": 100,
  "event_type": "wedding",
  "needs_event_room": true
}
```

**Response:**
```json
{
  "catering_analysis": { ... },
  "event_rooms": [ ... ],
  "summary_text": "..."
}
```

---

## 🐛 Troubleshooting

### Frontend won't start
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm start
```

### Backend not responding
```bash
docker compose logs api
docker compose restart api
```

### CORS errors
Check that API has CORS middleware enabled in `app/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Agent not extracting data
The agent uses regex patterns. Try being more explicit:
- ❌ "next month" → ✅ "March 15, 2025"
- ❌ "lots of people" → ✅ "100 guests"
- ❌ "somewhere in California" → ✅ "San Francisco"

---

## 🎯 Next Steps

### Immediate (This Week)
- [ ] Test with real users
- [ ] Fix any extraction bugs
- [ ] Add more cuisine types
- [ ] Improve response messages

### Short-term (Next Month)
- [ ] Integrate GPT-4 for better NLP
- [ ] Add voice input (speech recognition)
- [ ] Add image previews for venues
- [ ] Add map integration

### Long-term (3 Months)
- [ ] User authentication
- [ ] Booking system
- [ ] Payment integration
- [ ] Mobile app

---

## 📊 Success Metrics

Track these in your analytics:

- **Conversation completion rate**: % of users who complete all fields
- **Average messages to completion**: How many messages before search
- **Search success rate**: % of searches that return results
- **User satisfaction**: Ratings after search

---

## 🎓 Learning Resources

### For Developers
- [React Docs](https://react.dev)
- [FastAPI Docs](https://fastapi.tiangolo.com)
- [Framer Motion](https://www.framer.com/motion/)

### For Designers
- [Conversational UI Patterns](https://www.nngroup.com/articles/chatbots/)
- [Progressive Disclosure](https://www.nngroup.com/articles/progressive-disclosure/)

---

## 🤝 Contributing

Found a bug? Have an idea?

1. Open an issue on GitHub
2. Fork the repo
3. Make your changes
4. Submit a PR

---

## 📄 License

MIT - Use it however you want!

---

**Built with ❤️ for a better event planning experience**

**No forms. Just conversation. 🎉**
