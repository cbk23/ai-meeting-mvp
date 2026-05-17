# 🏃 Quick Start - Local Development

Get the app running on your machine in 5 minutes.

## Prerequisites

- **Python 3.9+** installed ([download](https://www.python.org))
- **Git** (optional, for cloning)
- **Gemini API Key** (from https://ai.google.dev)

## Setup

### 1. Clone/Download the Project

```bash
git clone <your-repo-url>
cd ai-meeting-mvp
```

### 2. Create Virtual Environment

```bash
# macOS/Linux
python3 -m venv venv
source venv/bin/activate

# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Windows (Command Prompt)
python -m venv venv
venv\Scripts\activate.bat
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup Environment Variables

```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your Gemini API key
# (on Windows, use: copy .env.example .env)
```

**Edit `.env`:**
```
GEMINI_API_KEY=your-actual-api-key-here
```

### 5. Run the App

```bash
python main.py
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### 6. Open in Browser

Visit: **http://localhost:8000**

🎉 **Done!** The app is running locally.

---

## Testing Features

### Test 1: Generate Notes (with Demo AI)
1. Type a meeting title
2. Paste a transcript in the textarea
3. Click "Generate AI Notes"
4. You'll see a demo response (or real AI if you have API key)

### Test 2: Chat
1. Select "Within current meeting"
2. Type a question like "What was discussed?"
3. Click "Ask"

### Test 3: Real AI (Optional)
- If you added your `GEMINI_API_KEY`, you'll get real AI responses
- Without it, you'll see demo responses (but everything works!)

---

## Docker (Optional)

To test with Docker locally:

```bash
# Build the image
docker build -t ai-meeting-mvp .

# Run the container
docker run -p 8000:8000 -e GEMINI_API_KEY=your-key ai-meeting-mvp
```

Visit: http://localhost:8000

---

## Stopping the App

Press **CTRL+C** in the terminal

---

## Troubleshooting

**Port 8000 already in use?**
```bash
# Use a different port
uvicorn main:app --port 8001
# Then visit: http://localhost:8001
```

**Import errors?**
```bash
# Make sure virtual environment is activated
# macOS/Linux: source venv/bin/activate
# Windows: venv\Scripts\activate

# Then reinstall
pip install -r requirements.txt
```

**API key not working?**
- Double-check you copied the entire key from https://ai.google.dev
- Make sure it's in the `.env` file (not quoted)
- Restart the app after changing `.env`

---

## Next Steps

✅ App working locally? Great! Now:

1. **Try different templates:** Standard, Agile, Executive
2. **Add more demo transcripts**
3. **Ready to deploy?** Follow [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)

---

## Useful Commands

```bash
# View app logs
tail -f app.log

# Check if Python packages are installed
pip list

# Update a package
pip install --upgrade google-generativeai

# Deactivate virtual environment
deactivate
```

Happy developing! 🚀
