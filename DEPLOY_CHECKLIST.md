# ✅ Deployment Checklist

Use this checklist to deploy your app in 10 minutes or less.

---

## 📋 Pre-Deployment (5 mins)

- [ ] **Get Gemini API Key**
  - [ ] Visit https://ai.google.dev
  - [ ] Click "Get API Key"
  - [ ] Create new project
  - [ ] Copy the API key (save somewhere safe)
  - [ ] **Estimated time:** 2 minutes

- [ ] **Prepare Your Code**
  - [ ] Create `.env` file from `.env.example`
  - [ ] Add `GEMINI_API_KEY=your-key` to `.env`
  - [ ] Test locally: `python main.py`
  - [ ] Visit http://localhost:8000 in browser
  - [ ] **Estimated time:** 3 minutes

---

## 🚀 Deployment to Railway (RECOMMENDED - 5 mins)

**Why Railway?** Fastest, easiest, free tier generous

### Step 1: Create Railway Account
- [ ] Go to https://railway.app
- [ ] Sign up with GitHub (easiest)
- [ ] Authorize Railway to access GitHub

### Step 2: Create New Project
- [ ] Click "Create New Project"
- [ ] Select "Deploy from GitHub"
- [ ] Select your `ai-meeting-mvp` repository

### Step 3: Configure & Deploy
- [ ] Railway auto-detects Python app ✨
- [ ] Wait for build to complete (~30 seconds)
- [ ] Click "Deployments" tab
- [ ] Railway should say "Success" ✅

### Step 4: Add API Key
- [ ] Click "Variables" tab
- [ ] Click "Add variable"
- [ ] **Key:** `GEMINI_API_KEY`
- [ ] **Value:** Paste your actual API key from earlier
- [ ] Click "Add"
- [ ] App auto-restarts with API key ✨

### Step 5: Get Your Live URL
- [ ] In Railway dashboard, find "Domains"
- [ ] You'll see something like: `https://ai-meeting-mvp-production.up.railway.app`
- [ ] Click the link to visit your live app! 🎉

**Total time: 5 minutes**

---

## 🟠 Deployment to Render (ALTERNATIVE - 7 mins)

### Step 1: Create Render Account
- [ ] Go to https://render.com
- [ ] Sign up with GitHub
- [ ] Authorize access

### Step 2: Create Web Service
- [ ] Click "New +"
- [ ] Select "Web Service"
- [ ] Select your `ai-meeting-mvp` repo

### Step 3: Configure
- [ ] **Name:** `ai-meeting-assistant`
- [ ] **Runtime:** Select "Python 3"
- [ ] **Build Command:** `pip install -r requirements.txt`
- [ ] **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Step 4: Add API Key
- [ ] Scroll to "Environment"
- [ ] Click "Add Environment Variable"
- [ ] **Key:** `GEMINI_API_KEY`
- [ ] **Value:** Paste your API key
- [ ] Click "Deploy" button

### Step 5: Wait for Deployment
- [ ] Build takes ~3-5 minutes
- [ ] When complete, Render gives you a URL
- [ ] Visit the URL to see your live app! 🎉

**Total time: 7 minutes**

---

## 🟣 Deployment to Heroku (ALTERNATIVE - 5 mins)

### Step 1: Setup
- [ ] Install Heroku CLI from https://devcenter.heroku.com/articles/heroku-cli
- [ ] Open terminal/command prompt
- [ ] Run: `heroku login`
- [ ] Browser opens for login

### Step 2: Create App
- [ ] Run: `heroku create ai-meeting-assistant`
- [ ] Heroku assigns you a URL

### Step 3: Add API Key
- [ ] Run: `heroku config:set GEMINI_API_KEY=your-actual-key-here`

### Step 4: Deploy
- [ ] Run: `git push heroku main`
- [ ] Wait for deployment (2-3 minutes)
- [ ] Get your URL from terminal output
- [ ] Visit URL to see your live app! 🎉

**Total time: 5 minutes**

---

## ✅ Post-Deployment Testing

Once your app is live:

### Test 1: UI Loads
- [ ] Visit your live URL
- [ ] See the MeetingAI interface
- [ ] Sidebar shows "Engineering", "Marketing" folders
- [ ] Sample meetings appear in history

### Test 2: Generate Notes
- [ ] Type a meeting title (e.g., "Team Sync")
- [ ] Paste a transcript:
  ```
  Alice: We need to ship the feature by Friday.
  Bob: I can start on the UI tomorrow.
  Alice: Great, let's sync Wednesday at 2pm.
  ```
- [ ] Select "Standard Template"
- [ ] Click "Generate AI Notes"
- [ ] You should see notes generated (demo or real, depending on API key)

### Test 3: Chat
- [ ] Type a question: "What was the deadline?"
- [ ] Click "Ask"
- [ ] AI responds with answer from transcript

### Test 4: Verify API Key Works (Optional)
- [ ] If AI responses look real (not demo placeholder), your API key works! ✨
- [ ] If you see "[DEMO MODE]", you forgot to set `GEMINI_API_KEY` variable

---

## 🎉 Success Criteria

All of these should be true:

- [ ] App loads at your live URL
- [ ] UI displays correctly (sidebar + main area)
- [ ] "Generate AI Notes" button works
- [ ] Chat feature responds to questions
- [ ] Data persists (meetings stay after page refresh)
- [ ] No error messages in browser console

**If all checked:** You're done! 🚀

---

## 🆘 If Something Goes Wrong

### App won't start / shows error
1. Check platform logs:
   - **Railway:** Deployments → Failed → View logs
   - **Render:** Logs tab
   - **Heroku:** `heroku logs --tail`
2. Look for: Python import errors, missing environment variable
3. Most common: Missing `GEMINI_API_KEY`

### AI features show "[DEMO MODE]"
1. You forgot to set `GEMINI_API_KEY` environment variable
2. Go to platform settings → Variables
3. Add: `GEMINI_API_KEY=your-actual-key`
4. App auto-restarts and tries again

### Page shows "Cannot GET /"
1. Make sure you're using the right URL (with https://)
2. Make sure it's fully deployed (not still building)
3. Try refreshing the page

### Still stuck?
- Review [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) for more details
- Check platform-specific docs (Railway, Render, Heroku)
- Look for error messages in logs

---

## 📊 Quick Reference

| Platform | Setup Time | Monthly Cost | Best For |
|----------|-----------|--------------|----------|
| **Railway** | 5 mins | Free tier | Quick MVP |
| **Render** | 7 mins | Free tier | Reliable |
| **Heroku** | 5 mins | $7-25+ | Production |

---

## 🎯 What's Next?

After deployment:

1. **Share your app** with team/stakeholders
2. **Test with real meeting transcripts**
3. **Gather feedback** on features
4. **Plan enhancements:**
   - User authentication
   - File upload support
   - Export as PDF
   - Search functionality

---

## 🚀 You Did It!

Congratulations! Your AI Meeting Assistant is live online. 

**Next steps:**
- Test with real meeting transcripts
- Share the URL with your team
- Start gathering feedback for v2

---

**Questions?** Check [README.md](./README.md) or [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)

**Happy deploying!** 🎉
