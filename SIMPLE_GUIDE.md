# Event Planner Agent - Simple Guide 🎉

## What Is This Project?

Think of this as **"Uber for Event Planning"** - but instead of booking rides, you're planning events!

### In Simple Words:

You tell the system:
- "I need to plan a wedding for 150 people in San Francisco"
- "Budget is $100 per person"
- "I want Italian food"

The system automatically:
1. **Finds real caterers** in San Francisco
2. **Finds real venues** that fit 150 people
3. **Calculates total costs**
4. **Shows you the best options**

### Real-World Example:

**Before (Manual Way):**
- Google "caterers in San Francisco" → 2 hours
- Call 10 caterers for quotes → 3 days
- Google "event venues" → 2 hours
- Visit 5 venues → 1 week
- Calculate costs in Excel → 1 hour
- **Total Time: 2+ weeks**

**After (This System):**
- Send one request to the API → **30 seconds**
- Get complete analysis with costs → **Done!**

---

## How Does It Work?

### The Magic Behind the Scenes:

```
You → API → AI Agent → Real Data Sources → Results
```

### Components (Like LEGO Blocks):

1. **Frontend** (What users see)
   - Website or mobile app
   - Simple form: date, location, guests, budget

2. **API** (The Brain)
   - FastAPI (Python web framework)
   - Processes your request
   - Talks to AI agents

3. **AI Agents** (The Workers)
   - Search for caterers
   - Search for venues
   - Calculate costs
   - Compare options

4. **Data Sources** (Where info comes from)
   - OpenStreetMap (free map data)
   - Nominatim (free address lookup)
   - Photon (free place search)

5. **Database** (Memory)
   - PostgreSQL (stores venues, caterers)
   - Redis (fast temporary storage)

---

## How to Use This (Step-by-Step)

### For Developers:

#### Step 1: Install Docker
```bash
# Mac
brew install docker

# Windows
# Download from docker.com

# Linux
sudo apt install docker.io docker-compose
```

#### Step 2: Clone the Project
```bash
git clone https://github.com/astrozeta7/event-planner-agent.git
cd event-planner-agent
```

#### Step 3: Start Everything
```bash
# Start all services (one command!)
docker compose up --build -d

# Wait 30 seconds for everything to start
```

#### Step 4: Test It
```bash
# Plan an event
curl -X POST http://localhost:8000/plan-event \
  -H "Content-Type: application/json" \
  -d '{
    "event_date": "2025-09-15",
    "location": "San Francisco",
    "number_of_guests": 120,
    "cuisine_preferences": ["Italian"],
    "budget_per_guest": 80,
    "needs_event_room": true
  }'
```

#### Step 5: See Results
Open browser: `http://localhost:8000/docs`

---

### For Non-Developers:

#### Option 1: Use the API Directly
1. Ask a developer to deploy it
2. Get the API URL (e.g., `https://api.eventplanner.com`)
3. Use tools like Postman or Insomnia
4. Send requests, get results

#### Option 2: Wait for the Website
1. We'll build a simple website
2. Fill out a form
3. Click "Plan Event"
4. See results instantly

---

## Current Status

### ✅ What's Working (V2.1):

- **Real-time data** from OpenStreetMap
- **Free geocoding** (no API keys!)
- **Cost calculations**
- **Venue matching**
- **Caterer search**
- **Docker deployment**

### 🚧 What's Missing (For Public Launch):

1. **User Interface** (Website/App)
2. **User Accounts** (Login/Signup)
3. **Payment Processing** (Stripe/PayPal)
4. **Booking System** (Reserve venues/caterers)
5. **Email Notifications**
6. **Mobile App**
7. **Admin Dashboard**

---

## How to Make This Public (Roadmap)

### Phase 1: MVP (Minimum Viable Product) - 2 Weeks

**Goal:** Get 10 beta users

**Tasks:**
1. ✅ Backend API (Done!)
2. ⏳ Simple React website
3. ⏳ User authentication (Firebase)
4. ⏳ Deploy to cloud (AWS/Heroku)
5. ⏳ Custom domain (eventplanner.com)

**Cost:** $20/month (hosting)

---

### Phase 2: Beta Launch - 1 Month

**Goal:** Get 100 paying users

**Tasks:**
1. ⏳ Payment integration (Stripe)
2. ⏳ Booking system
3. ⏳ Email notifications (SendGrid)
4. ⏳ Admin dashboard
5. ⏳ Analytics (Google Analytics)
6. ⏳ SEO optimization

**Cost:** $100/month (hosting + services)

---

### Phase 3: Public Launch - 3 Months

**Goal:** Get 1,000+ users

**Tasks:**
1. ⏳ Mobile app (React Native)
2. ⏳ Advanced AI features
3. ⏳ Vendor partnerships
4. ⏳ Marketing campaign
5. ⏳ Customer support system
6. ⏳ Multi-language support

**Cost:** $500/month (scaling infrastructure)

---

## Technical Improvements Needed

### 1. Frontend (User Interface)

**Current:** None (API only)

**Needed:**
```
React Website
├── Landing Page
├── Event Planning Form
├── Results Page
├── User Dashboard
└── Booking Page
```

**Time:** 2 weeks  
**Cost:** Free (open source)

---

### 2. Authentication

**Current:** None (anyone can use API)

**Needed:**
- User signup/login
- Email verification
- Password reset
- OAuth (Google/Facebook login)

**Tools:** Firebase Auth (free tier)  
**Time:** 3 days

---

### 3. Payment System

**Current:** None

**Needed:**
- Credit card processing
- Subscription plans
- Invoicing
- Refunds

**Tools:** Stripe ($0.30 + 2.9% per transaction)  
**Time:** 1 week

---

### 4. Booking System

**Current:** Just shows options

**Needed:**
- Reserve venues
- Book caterers
- Calendar integration
- Confirmation emails
- Cancellation handling

**Time:** 2 weeks

---

### 5. Cloud Deployment

**Current:** Runs on your computer

**Needed:**
- Cloud hosting (AWS/Heroku/DigitalOcean)
- Auto-scaling
- Load balancing
- CDN for fast loading
- SSL certificate (HTTPS)

**Cost:** $20-100/month  
**Time:** 3 days

---

### 6. Monitoring & Analytics

**Current:** None

**Needed:**
- Error tracking (Sentry)
- Performance monitoring
- User analytics
- A/B testing

**Tools:** 
- Sentry (free tier)
- Google Analytics (free)
- Mixpanel (free tier)

**Time:** 2 days

---

### 7. Security

**Current:** Basic

**Needed:**
- Rate limiting (prevent abuse)
- API key authentication
- Data encryption
- GDPR compliance
- Security audits

**Time:** 1 week

---

### 8. Data Quality

**Current:** Raw OpenStreetMap data

**Needed:**
- Data validation
- Duplicate removal
- Photo scraping
- Review aggregation
- Business verification

**Time:** 2 weeks

---

## Business Model (How to Make Money)

### Option 1: Freemium

- **Free:** 3 event plans per month
- **Pro ($9.99/month):** Unlimited plans + booking
- **Business ($49/month):** Multiple users + analytics

### Option 2: Commission

- **Free for users**
- **Take 5-10% commission** from venues/caterers
- Partner with vendors

### Option 3: Subscription for Vendors

- **Free for users**
- **Vendors pay $99/month** to be listed
- Premium placement for higher tiers

---

## Quick Start Checklist

### For Developers:

- [ ] Install Docker
- [ ] Clone repository
- [ ] Run `docker compose up`
- [ ] Test API at `localhost:8000/docs`
- [ ] Read code in `app/` folder
- [ ] Make improvements
- [ ] Submit pull request

### For Business People:

- [ ] Understand the concept
- [ ] Define target market
- [ ] Create business plan
- [ ] Find developers
- [ ] Set budget ($5K-20K for MVP)
- [ ] Launch beta
- [ ] Get feedback
- [ ] Iterate

---

## Cost Breakdown (To Launch)

### Development Costs:

| Item | Cost | Time |
|------|------|------|
| Backend (Done!) | $0 | ✅ |
| Frontend Website | $0 (DIY) or $2K (hire) | 2 weeks |
| Mobile App | $0 (DIY) or $5K (hire) | 1 month |
| Design/UX | $0 (templates) or $1K | 1 week |
| **Total Dev** | **$0-8K** | **1-2 months** |

### Monthly Operating Costs:

| Service | Cost |
|---------|------|
| Cloud Hosting (AWS/Heroku) | $20-100 |
| Domain Name | $12/year |
| SSL Certificate | Free (Let's Encrypt) |
| Email Service (SendGrid) | $15 |
| Database Backup | $10 |
| Monitoring (Sentry) | Free tier |
| **Total Monthly** | **$45-125** |

### Marketing Costs:

| Channel | Cost |
|---------|------|
| Google Ads | $500-2K/month |
| Social Media | $200-1K/month |
| Content Marketing | Free (DIY) |
| SEO | Free (DIY) or $500/month |
| **Total Marketing** | **$700-3.5K/month** |

---

## Success Metrics

### Month 1:
- 10 beta users
- 50 event plans created
- 5 bookings

### Month 3:
- 100 active users
- 500 event plans
- 50 bookings
- $500 revenue

### Month 6:
- 1,000 active users
- 5,000 event plans
- 500 bookings
- $5,000 revenue

### Year 1:
- 10,000 active users
- 50,000 event plans
- 5,000 bookings
- $50,000 revenue

---

## FAQ

### Q: Do I need to pay for APIs?
**A:** No! We use 100% free data sources (OpenStreetMap, Nominatim, Photon).

### Q: Can I use this for my business?
**A:** Yes! It's open source. You can modify and commercialize it.

### Q: How accurate is the data?
**A:** OpenStreetMap has 8+ billion data points. Accuracy varies by location (best in US/Europe).

### Q: Can I add my own data sources?
**A:** Yes! The architecture is modular. Add new MCP servers easily.

### Q: Is this production-ready?
**A:** Backend: Yes. Frontend: No (needs to be built).

### Q: How do I get support?
**A:** GitHub Issues or email the maintainer.

---

## Next Steps

### For You (Right Now):

1. **Try it locally:**
   ```bash
   docker compose up -d
   curl http://localhost:8000/docs
   ```

2. **Explore the code:**
   - `app/main.py` - API endpoints
   - `app/services/` - Business logic
   - `mcp-servers/` - Data sources

3. **Make improvements:**
   - Add new features
   - Fix bugs
   - Improve documentation

4. **Share feedback:**
   - What's confusing?
   - What's missing?
   - What would you pay for?

---

## Resources

### Learn More:
- [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)
- [Docker Basics](https://docs.docker.com/get-started/)
- [OpenStreetMap](https://www.openstreetmap.org/)
- [React Tutorial](https://react.dev/learn)

### Tools You'll Need:
- Code Editor: VS Code (free)
- API Testing: Postman (free)
- Design: Figma (free)
- Hosting: Heroku/AWS (free tier)

---

## Contact

- **GitHub:** https://github.com/astrozeta7/event-planner-agent
- **Issues:** https://github.com/astrozeta7/event-planner-agent/issues
- **Branch:** `dev/v2.1` (latest features)

---

**Built with ❤️ using 100% free and open-source tools!**
