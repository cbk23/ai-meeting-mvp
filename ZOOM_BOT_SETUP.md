# 🤖 Zoom Bot Feature - Quick Setup Guide

Get your custom Zoom recording bot running in 1-2 hours.

---

## 📋 Checklist

- [ ] Step 1: Get Zoom API credentials (15 mins)
- [ ] Step 2: Install dependencies (5 mins)
- [ ] Step 3: Add code files to project (5 mins)
- [ ] Step 4: Configure environment (5 mins)
- [ ] Step 5: Test locally (20 mins)
- [ ] Step 6: Deploy (10 mins)

---

## 🔑 Step 1: Get Zoom API Credentials (15 mins)

### 1.1 Create Zoom OAuth App

```
1. Go to: https://marketplace.zoom.us
2. Sign in (create account if needed)
3. Top menu → "Develop" → "Build App"
4. App type: Select "Bot Account"
5. Name: "Meeting Recording Bot"
6. Create app
```

### 1.2 Get Credentials

After creation, you'll see:
- **Client ID** - Copy this
- **Client Secret** - Copy this
- **Bot JID** - Copy this (usually in Settings)

```bash
# Save to .env
ZOOM_CLIENT_ID=your-client-id-here
ZOOM_CLIENT_SECRET=your-client-secret-here
ZOOM_BOT_JID=your-bot-jid-here
```

### 1.3 Enable Bot Scopes

In your Zoom app settings:
```
1. Click "Scopes" tab
2. Add these OAuth scopes:
   ☑ meeting:bot:read
   ☑ meeting:bot:create
   ☑ meeting:bot:delete
   ☑ meeting:read
3. Save
```

---

## 📦 Step 2: Install Dependencies (5 mins)

```bash
# Option A: Use requirements-with-bot.txt (includes everything)
pip install -r requirements-with-bot.txt

# Option B: Add to existing requirements.txt
pip install requests PyJWT openai-whisper

# Install system dependency
# macOS:
brew install ffmpeg

# Ubuntu/Debian:
sudo apt-get install ffmpeg

# Windows:
# Download from https://ffmpeg.org/download.html
```

---

## 💻 Step 3: Add Code Files to Project (5 mins)

Copy these new files to your project root:

```
your-project/
├── main.py                    (update with bot endpoints)
├── templates.html             (update with bot UI)
├── zoom_bot_service.py        (NEW - add this)
├── transcription_service.py   (NEW - add this)
├── requirements.txt           (update)
└── .env                       (update)
```

### Files to Add/Update:

1. **zoom_bot_service.py** - Zoom API integration
2. **transcription_service.py** - Audio transcription
3. **main.py** - Add bot endpoints (see CUSTOM_ZOOM_BOT.md)
4. **templates.html** - Add bot UI (see CUSTOM_ZOOM_BOT.md)
5. **requirements.txt** - Add dependencies

---

## ⚙️ Step 4: Configure Environment (5 mins)

Update `.env` file:

```bash
# Existing
GEMINI_API_KEY=your-gemini-key

# NEW - Zoom Bot
ZOOM_CLIENT_ID=your-zoom-client-id
ZOOM_CLIENT_SECRET=your-zoom-client-secret
ZOOM_BOT_JID=your-bot-jid

# Transcription backend
TRANSCRIPTION_BACKEND=local  # Use "cloud" for AssemblyAI instead

# If using AssemblyAI for cloud transcription (optional)
# ASSEMBLYAI_API_KEY=your-assemblyai-key
```

---

## 🧪 Step 5: Test Locally (20 mins)

### 5.1 Start Your App

```bash
# Make sure virtual environment is activated
python main.py

# Should see:
# INFO:     Uvicorn running on http://127.0.0.1:8000
```

### 5.2 Test Bot Status

```bash
# In another terminal, check if bot is configured
curl http://localhost:8000/api/bot/status

# Should return:
# {
#   "status": "configured",
#   "zoom_configured": true,
#   "transcription_backend": "local",
#   "gemini_configured": true
# }
```

### 5.3 Test with Sample Meeting

```bash
# 1. Create a test Zoom meeting
#    Go to Zoom, start a test meeting
#    Get the Meeting ID from URL

# 2. Send request to add bot
curl -X POST http://localhost:8000/api/bot/add-to-zoom \
  -H "Content-Type: application/json" \
  -d '{"zoom_meeting_id": "123456789", "meeting_title": "Test Meeting"}'

# 3. Check response
# Should see: {"status": "success", "message": "Bot added to meeting"}

# 4. View UI at http://localhost:8000
# Fill in Zoom Meeting ID
# Click "Add Bot to Meeting"
```

### 5.4 Test Audio Transcription

```bash
# Get a sample audio file or record one
# Then in your app, upload and process it
# Check http://localhost:8000 → Zoom Bot Recording section
```

---

## 🚀 Step 6: Deploy (10 mins)

### For Railway:

```
1. Go to: https://railway.app
2. In dashboard → Variables
3. Add these variables:
   - ZOOM_CLIENT_ID = your-id
   - ZOOM_CLIENT_SECRET = your-secret
   - ZOOM_BOT_JID = your-jid
   - TRANSCRIPTION_BACKEND = local
4. Redeploy from GitHub
```

### For Render:

```
1. Go to: https://render.com
2. Dashboard → Environment
3. Add variables (same as Railway)
4. Redeploy
```

### For Heroku:

```bash
heroku config:set ZOOM_CLIENT_ID=your-id
heroku config:set ZOOM_CLIENT_SECRET=your-secret
heroku config:set ZOOM_BOT_JID=your-jid
heroku config:set TRANSCRIPTION_BACKEND=local
git push heroku main
```

---

## ✅ Verify Deployment

After deploying:

```bash
# Check bot status at your live URL
curl https://your-app.herokuapp.com/api/bot/status

# Should return configured status
```

---

## 🎯 How It Works

### User Flow:

```
1. User has a Zoom meeting scheduled
2. User gets the Zoom Meeting ID
3. User goes to your app → "Zoom Bot Recording"
4. Enters Meeting ID → Clicks "Add Bot to Meeting"
5. Bot automatically joins when meeting starts
6. Bot records the entire meeting
7. Meeting ends → Recording saved
8. User uploads recording file to app
9. App transcribes audio (Whisper)
10. Transcript sent to Gemini AI
11. AI generates summary
12. Everything saved to dashboard
```

---

## 📊 Transcription Options

### Local (Whisper) - RECOMMENDED

✅ **Pros:**
- Free
- Offline (no internet needed for transcription)
- No cost per use
- Privacy (stays on your server)

❌ **Cons:**
- Slower (first run downloads ~1.4GB model)
- Slightly less accurate than cloud
- Uses more CPU

**Setup:**
```bash
pip install openai-whisper
TRANSCRIPTION_BACKEND=local
```

### Cloud (AssemblyAI) - OPTIONAL

✅ **Pros:**
- More accurate
- Faster
- Speaker identification included

❌ **Cons:**
- Costs ~$0.10-0.50 per hour of audio
- Requires internet
- Requires API key

**Setup:**
```bash
pip install assemblyai
TRANSCRIPTION_BACKEND=cloud
ASSEMBLYAI_API_KEY=your-key
```

---

## 🔄 Workflow Example

### Complete Example:

```
User Action: Join Zoom → Chat about project → Meeting ends
    ↓
App: Bot was recording whole time
    ↓
User: Uploads recording to app
    ↓
App: Transcribes with Whisper (5-10 mins depending on length)
    ↓
App: Sends to Gemini AI
    ↓
App: Generates summary, action items, key decisions
    ↓
Result: Meeting in dashboard with:
- Full transcript
- AI summary
- Chat about meeting
- Search & export options
```

---

## 🐛 Troubleshooting

### "Bot won't join meeting"
```
Check:
1. Zoom Client ID & Secret are correct
2. Bot has proper scopes in Zoom app settings
3. Meeting ID format is numeric (no hyphens)
4. Your Zoom account has API access enabled
```

### "Transcription fails"
```
Check:
1. Audio file exists and is readable
2. FFmpeg is installed (ffmpeg --version)
3. Audio format is supported (.mp3, .wav, .m4a, etc)
4. For Whisper: Try with a shorter audio file
5. For AssemblyAI: Check API key is valid
```

### "Meeting ID not found"
```
Check:
1. You're using the numeric Meeting ID (not the link)
2. The meeting actually exists
3. Your Zoom account can access the meeting
```

---

## 📈 Next Steps

### Short Term (This Week)
1. ✅ Bot working locally
2. ✅ Test with real recordings
3. ✅ Deploy to cloud
4. ✅ Get user feedback

### Medium Term (This Month)
1. Add Google Meet support
2. Add speaker identification
3. Add meeting transcripts search
4. Automatic meeting scheduling

### Long Term (This Quarter)
1. Multi-user support
2. Meeting analytics
3. Team collaboration features
4. Integration with Slack/Email

---

## 📞 Quick Links

- **Zoom API Docs:** https://developers.zoom.us/docs/
- **Whisper Docs:** https://github.com/openai/whisper
- **AssemblyAI Docs:** https://www.assemblyai.com/docs
- **Your Custom Bot Guide:** See `CUSTOM_ZOOM_BOT.md`

---

## 🎉 You're Ready!

You now have:
- ✅ Custom Zoom bot code
- ✅ Local & cloud transcription
- ✅ Integration with your app
- ✅ Deployment configs
- ✅ Complete documentation

**Next step:** Follow the 6-step checklist above to get it running!

---

**Questions?** Check `CUSTOM_ZOOM_BOT.md` for detailed explanation of each component.
