@echo off
REM Quick GitHub Push Script for Arc Project

cd "C:\Users\sumuk\Documents\Personal\PythonProjects\Hackathon\Arc - Image to Model Tool"

REM Check if git is initialized
if not exist .git (
    echo Initializing git repository...
    git init
)

REM Add all files
echo Adding files to git...
git add .

REM Commit
echo Committing changes...
git commit -m "Arc - Image to Model Tool - Update %date% %time%"

REM Check if remote exists
git remote get-url origin >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ===== IMPORTANT =====
    echo You need to create a GitHub repository first!
    echo.
    echo 1. Go to https://github.com/new
    echo 2. Create a repository named 'arc-image-to-model'
    echo 3. Copy the URL from GitHub
    echo 4. Run this command:
    echo    git remote add origin [PASTE_YOUR_GITHUB_URL_HERE]
    echo 5. Then run this script again
    echo.
    pause
    exit /b 1
)

REM Push to GitHub
echo Pushing to GitHub...
git push -u origin master

echo.
echo ===== SUCCESS =====
echo Code pushed to GitHub!
echo.
echo Next steps:
echo 1. Go to https://replit.com
echo 2. Click "Create Repl"
echo 3. Choose "Import from GitHub"
echo 4. Paste your GitHub URL
echo 5. Click "Run"
echo.
pause
