@echo off
REM NotebookLM RAG System Setup Script for Windows
REM This script helps you set up the development environment quickly

echo 🚀 Setting up NotebookLM RAG System...
echo =======================================

REM Function to check if command exists
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Python is required but not installed.
    exit /b 1
)

where node >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Node.js is required but not installed.
    exit /b 1
)

where docker >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Docker is required but not installed.
    exit /b 1
)

where docker-compose >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Docker Compose is required but not installed.
    exit /b 1
)

echo ✅ All prerequisites are installed.

REM Create environment files
echo 📄 Creating environment files...

if not exist "backend\.env" (
    if exist "backend\.env.example" (
        copy "backend\.env.example" "backend\.env" >nul
        echo ✅ Created backend\.env from template
    ) else (
        echo ⚠️  backend\.env.example not found, creating basic .env
        (
        echo # Database
        echo DATABASE_URL=postgresql://postgres:password@localhost:5432/notebooklm_rag
        echo.
        echo # Security
        echo SECRET_KEY=your-super-secret-key-change-this-in-production
        echo ALGORITHM=HS256
        echo ACCESS_TOKEN_EXPIRE_MINUTES=30
        echo.
        echo # Google Cloud
        echo GOOGLE_APPLICATION_CREDENTIALS=./credentials/service-account.json
        echo GOOGLE_CLOUD_PROJECT=your-project-id
        echo.
        echo # Redis
        echo REDIS_URL=redis://localhost:6379
        echo.
        echo # Environment
        echo ENVIRONMENT=development
        echo LOG_LEVEL=INFO
        ) > "backend\.env"
    )
) else (
    echo ✅ backend\.env already exists
)

if not exist "frontend\.env.local" (
    if exist "frontend\.env.example" (
        copy "frontend\.env.example" "frontend\.env.local" >nul
        echo ✅ Created frontend\.env.local from template
    ) else (
        echo ⚠️  frontend\.env.example not found, creating basic .env.local
        (
        echo NEXT_PUBLIC_API_URL=http://localhost:8000
        echo NEXT_PUBLIC_APP_NAME=NotebookLM RAG System
        echo NEXTAUTH_SECRET=your-nextauth-secret-change-this
        echo NEXTAUTH_URL=http://localhost:3000
        ) > "frontend\.env.local"
    )
) else (
    echo ✅ frontend\.env.local already exists
)

REM Create credentials directory
echo 📁 Creating credentials directory...
if not exist "backend\credentials" mkdir "backend\credentials"

REM Setup backend
echo 🐍 Setting up Python backend...
cd backend

if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing Python dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

echo ✅ Backend setup complete
cd ..

REM Setup frontend
echo ⚛️  Setting up React frontend...
cd frontend

echo Installing Node.js dependencies...
npm install

echo ✅ Frontend setup complete
cd ..

echo.
echo ✅ Setup completed successfully!
echo.
echo 🎯 Next steps:
echo 1. Configure Google Cloud credentials:
echo    - Place your service account JSON file in backend\credentials\
echo    - Update GOOGLE_APPLICATION_CREDENTIALS in backend\.env
echo.
echo 2. Start the application:
echo    Option A - Docker (Recommended):
echo    $ docker-compose up -d
echo.
echo    Option B - Local development:
echo    Terminal 1: cd backend ^&^& venv\Scripts\activate ^&^& uvicorn app.main:app --reload
echo    Terminal 2: cd frontend ^&^& npm run dev
echo.
echo 3. Access the application:
echo    - Frontend: http://localhost:3000
echo    - Backend API: http://localhost:8000
echo    - API Docs: http://localhost:8000/docs
echo.
echo 🚀 Happy coding!

pause
