# Deploy Arc to Replit - Step by Step

## Quick Setup (5 minutes)

### Step 1: Create a GitHub Repository
Since Replit imports from GitHub, you need to upload your code there first.

1. Go to https://github.com/new
2. Create a repository named `arc-image-to-model`
3. Clone it to your computer (or use this project)

### Step 2: Upload Code to GitHub

```bash
cd "C:\Users\sumuk\Documents\Personal\PythonProjects\Hackathon\Arc - Image to Model Tool"

# Initialize git (if not already done)
git init
git add .
git commit -m "Initial commit: Arc - Image to Model Tool"

# Add your GitHub repo as remote
git remote add origin https://github.com/YOUR_USERNAME/arc-image-to-model.git
git branch -M main
git push -u origin main
```

### Step 3: Import to Replit

1. Go to https://replit.com
2. Sign up/Login
3. Click "Create Repl"
4. Choose "Import from GitHub"
5. Paste: `https://github.com/YOUR_USERNAME/arc-image-to-model`
6. Click "Import"
7. Click "Run" button

### Step 4: Test on Phone

1. Copy the Replit URL (it will be something like `https://arc-image-to-model.YOUR_USERNAME.repl.co`)
2. Open it on your phone's browser
3. Click "Start Camera"
4. Take photos to scan walls

---

## What Gets Deployed

✅ FastAPI Backend
✅ HTML Frontend with Camera
✅ AI Models (wall detection, element detection)
✅ All dependencies (opencv, numpy, etc.)

---

## Environment Variables (if needed later)

If you need to add any, go to Replit → Tools → Secrets

---

## Troubleshooting

**App won't start?**
- Check the console for errors
- Make sure `requirements.txt` is in the root and backend folder

**Camera not working?**
- Need HTTPS (Replit provides this)
- Replit URL uses HTTPS automatically

**Models not found?**
- Make sure `models/` folder is in the root

---

## Next Steps After Deploy

1. Share the Replit URL with others
2. Test on multiple devices
3. Improve AI models in `models/` folder
4. Push changes to GitHub
5. Replit will auto-update

**Your Replit URL will be public and shareable!**
