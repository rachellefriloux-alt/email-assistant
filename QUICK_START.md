# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Install Dependencies (2 min)

**Backend**:
```bash
cd backend
pip install -r requirements.txt
```

**Frontend**:
```bash
cd frontend
npm install
```

### Step 2: Setup Gemini API (1 min)

Create `backend/.env`:
```env
GEMINI_API_KEY=your_api_key_here
```

Get free API key: https://makersuite.google.com/app/apikey

### Step 3: Start Backend (1 min)

```bash
cd backend
uvicorn app:app --reload --port 8000
```

You should see:
```
Uvicorn running on http://127.0.0.1:8000
```

### Step 4: Start Frontend (1 min)

In a new terminal:
```bash
cd frontend
npm run dev
```

You should see:
```
Local:   http://localhost:5173
```

### Step 5: Open Browser

Visit: **http://localhost:5173**

---

## 🧪 Test the Features

### Demo Mode (Works Immediately!)
1. Open the app
2. Click any email to read it
3. Click "Summarize" or "Extract Actions"
4. Click "Compose" and try the "Magic Polish" buttons

**No backend needed for demo!**

### Live API Mode
1. Click Settings gear (bottom left)
2. Toggle "Demo Mode" OFF
3. Try all features again - now using real API

---

## 🎨 What You Get

### Frontend
- ✨ Glassmorphic UI with smooth animations
- 🌓 Full dark mode support
- 📱 Responsive mobile design
- 📊 Analytics dashboard
- 🎯 Urgency detection badges
- 💬 AI-powered email composer
- ✅ Bulk email actions

### Backend
- 🧠 Sentiment analysis (Positive/Negative/Neutral)
- 🚨 Urgency detection (High/Normal)
- 📧 Smart categorization
- ✨ Gemini AI integration:
  - Summarization
  - Action item extraction
  - Draft rewriting (3 tones)

---

## 📂 Project Structure

```
email-assistant/
├── frontend/                 # React app
│   ├── src/
│   │   └── App.jsx          # ✨ NEW - Completely rewritten
│   ├── package.json
│   └── ...
├── backend/                  # Python FastAPI
│   ├── services/
│   │   ├── ai_service.py     # ✅ UPDATED - Sentiment + Urgency
│   │   ├── gemini_service.py # ✨ NEW - Gemini integration
│   │   └── ...
│   ├── models/
│   │   └── email.py          # ✅ UPDATED - New fields
│   ├── routes/
│   │   └── assistant.py      # ✅ UPDATED - New endpoints
│   ├── requirements.txt       # ✅ UPDATED - google-generativeai
│   └── ...
├── IMPLEMENTATION_SUMMARY.md # 📖 Full documentation
├── IMPLEMENTATION_CHECKLIST.md # ✅ Detailed checklist
└── QUICK_START.md            # 👈 You are here
```

---

## 🔧 Common Issues & Fixes

### "Module not found: google-generativeai"
```bash
pip install google-generativeai==0.4.1
```

### "GEMINI_API_KEY not found"
1. Create `backend/.env`
2. Add: `GEMINI_API_KEY=your_key`
3. Restart backend

### "Port 8000 already in use"
```bash
uvicorn app:app --reload --port 8001
```
Then update `API_BASE` in `frontend/src/App.jsx` line ~277

### Frontend won't load
- Clear browser cache (Cmd+Shift+R or Ctrl+Shift+R)
- Check console (F12) for CORS errors
- Ensure backend is running on port 8000

---

## 📖 Full Documentation

See:
- **IMPLEMENTATION_SUMMARY.md** - Complete feature overview and API docs
- **IMPLEMENTATION_CHECKLIST.md** - Detailed checklist of all changes

---

## 💡 Tips

### Test Without Backend
1. Just run `npm run dev`
2. Demo mode works instantly
3. No API needed!

### Customize Colors
Edit `frontend/src/App.jsx` → `Badge` component colors

### Add Gemini Prompts
Edit `backend/services/gemini_service.py` functions

### Change Email Categories
Edit `backend/services/ai_service.py` → `FALLBACK_KEYWORDS`

---

## 🎉 You're All Set!

Your email-assistant is now equipped with:
- Advanced AI analysis
- Gorgeous polished UI
- Gemini integration
- Demo mode for testing

**Happy emailing!** ✉️

---

## 📞 Need Help?

1. Check **IMPLEMENTATION_SUMMARY.md** for detailed docs
2. Review error messages in console/terminal
3. Verify environment variables are set
4. Restart both frontend and backend

---

**Status**: ✅ Ready to go!

Visit **http://localhost:5173** and start exploring.
