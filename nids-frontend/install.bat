@echo off
echo Installing NIDS Frontend Dependencies...
echo.

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Node.js is not installed. Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

REM Check if npm is available
npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: npm is not available. Please ensure Node.js is properly installed.
    pause
    exit /b 1
)

echo Node.js version:
node --version
echo.

echo Installing dependencies...
npm install

if %errorlevel% neq 0 (
    echo Error: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Installation completed successfully!
echo.
echo Next steps:
echo 1. Set up your Clerk account at https://clerk.com
echo 2. Create a .env.local file with your Clerk keys
echo 3. Run: npm run dev
echo.
echo Creating .env.local template...
if not exist .env.local (
    copy env-template.txt .env.local
    echo .env.local file created! Please edit it with your Clerk API keys.
) else (
    echo .env.local already exists. Skipping creation.
)
echo.
echo IMPORTANT: You must add your Clerk API keys to .env.local before running the app!
echo.
pause

