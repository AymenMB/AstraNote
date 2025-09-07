 # AstraNote — Enterprise RAG Platform

 [![Status](https://img.shields.io/badge/status-active-brightgreen)](https://github.com/your-org/notebooklm)
 [![License](https://img.shields.io/badge/license-MIT-blue.svg)](./LICENSE)

 AstraNote (recommended name) is a production-ready Retrieval-Augmented Generation (RAG) platform that integrates Google NotebookLM with a FastAPI backend, a Next.js frontend, and PostgreSQL for durable storage. It provides secure user management, document ingestion, query history, and audit logging — built for teams and enterprises who want contextual Q&A over private knowledge.

 Why "AstraNote"? The name conveys a bright, organized beacon for knowledge — combining document-first workflows with reliable retrieval and generative capabilities.

 Quick name alternatives (pick one): AstraNote (recommended), NoteForge, LuminaRAG, AtlasNote, QueryNest, Notebase AI.

 ---

 ## Highlights

 - Secure authentication (JWT + refresh tokens)
 - Document ingestion: PDF, text and other formats
 - RAG queries using Google NotebookLM as the LLM backend
 - Audit logs and query history for compliance
 - Dockerized for single-command local and production deployments
 - Interactive API docs (Swagger) and modern Next.js UI

 ## Local quickstart (Docker, recommended)

 Prerequisites

 - Docker & Docker Compose

 Launch (PowerShell)

 ```powershell
 cd 'd:\al jaw\notebooklm'
 docker-compose up -d --build
 docker-compose ps
 docker-compose logs -f
 ```

 Default URLs

 - Frontend: http://localhost:3000
 - Backend API: http://localhost:8000
 - API docs (Swagger): http://localhost:8000/docs

 ## Local dev (no Docker) — backend + frontend

 1) Backend

 ```powershell
 cd backend
 python -m venv .venv
 .\.venv\Scripts\Activate.ps1    # PowerShell
 pip install -r requirements.txt
 alembic upgrade head
 uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
 ```

 2) Frontend

 ```powershell
 cd frontend
 npm install
 npm run dev
 ```

 3) Database (manual)

 ```powershell
 createdb notebooklm_rag
 psql -d notebooklm_rag -f database/init.sql
 ```

 ## Configuration

 Copy and customize environment templates before running locally.

 Backend (`backend/.env`)

 ```env
 DATABASE_URL=postgresql://user:password@localhost:5432/notebooklm_rag
 SECRET_KEY=your-secret-key
 ALGORITHM=HS256
 ACCESS_TOKEN_EXPIRE_MINUTES=30
 GOOGLE_APPLICATION_CREDENTIALS=./credentials/service-account.json
 GOOGLE_CLOUD_PROJECT=your-project-id
 REDIS_URL=redis://localhost:6379
 ENVIRONMENT=development
 LOG_LEVEL=INFO
 ```

 Frontend (`frontend/.env.local`)

 ```env
 NEXT_PUBLIC_API_URL=http://localhost:8000
 NEXT_PUBLIC_APP_NAME=AstraNote
 NEXTAUTH_SECRET=your-nextauth-secret
 NEXTAUTH_URL=http://localhost:3000
 ```

 Notes: create a Google Cloud service account with NotebookLM API access, download the JSON key, and place it at `backend/credentials/service-account.json`.

 ## Architecture

 - Frontend: Next.js (app router) + React components
 - Backend: FastAPI, pydantic schemas, SQLAlchemy & Alembic
 - LLM: Google NotebookLM via service account
 - Storage: PostgreSQL for metadata; extendable to vector stores
 - Cache: Redis for ephemeral cache and rate limiting (optional)
 - Orchestration: Docker Compose for local and production

 ## API summary

 Core endpoints

 - POST /api/auth/register — register
 - POST /api/auth/login — login (access & refresh tokens)
 - POST /api/documents/upload — upload documents
 - GET /api/documents — list documents
 - POST /api/queries — run a RAG query
 - GET /api/queries — list query history

 See Swagger UI at `/docs` for full API details.

 ## Security & privacy

 - Short-lived JWT access tokens and refresh tokens
 - Role-based access control (admin / user)
 - Audit logs for uploads, queries, and admin actions
 - Optionally enable encryption at rest for uploaded files and secrets in production environments

 ## Tests

 Backend

 ```powershell
 cd backend
 pytest tests/ -v
 ```

 Frontend

 ```powershell
 cd frontend
 npm test
 ```

 ## Deployment

 Production with Docker Compose

 ```powershell
 docker-compose -f docker-compose.prod.yml build
 docker-compose -f docker-compose.prod.yml up -d
 ```

 Cloud-ready: Cloud Run, GKE, AWS ECS, Azure Container Instances, or Kubernetes.

 ## Troubleshooting

 - Reinstall deps: `pip install -r backend/requirements.txt`, `npm install`
 - DB connection: verify `DATABASE_URL`, ensure DB is running
 - Google API: verify service account, enable NotebookLM API, check IAM
 - View logs:

 ```powershell
 docker-compose logs --tail=200 backend
 ```

 ## Project layout (top-level)

 ```text
 backend/        # FastAPI app, models, services, tests
 frontend/       # Next.js UI
 database/       # schema and init scripts
 docker/         # helpers and Docker-related files
 docker-compose.yml
 docker-compose.prod.yml
 README.md
 ```

 ## Contributing

 1. Fork
 2. Create a feature branch
 3. Add tests
 4. Open a PR with a clear description

 High-impact contributions: additional ingestion parsers, vector store integrations, enterprise auth connectors, and UX improvements for query workflows.

 ## License

 MIT — see `LICENSE`.

 ---

 Next steps I can help with:

 - Rename project files and metadata to your chosen app name (package.json, Next app title, README references).
 - Add a short CONTRIBUTING.md and CODE_OF_CONDUCT.md.
 - Insert a screenshot or demo GIF into the README.

 Pick the name you prefer (AstraNote recommended) and tell me which follow-up you'd like next.
# NotebookLM RAG System

A production-ready Retrieval-Augmented Generation (RAG) system built with Google's NotebookLM API, featuring a FastAPI backend, React frontend, and PostgreSQL database.

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Docker & Docker Compose
- Google Cloud Account with NotebookLM API access

### Environment Setup

1. **Navigate to the Project**

   ```bash
   cd "d:\al jaw\notebooklm"
   ```

2. **Create Environment Files**

   Backend `.env`:

   ```bash
   # Copy and customize
   cp backend/.env.example backend/.env
   ```

   Frontend `.env.local`:

   ```bash
   # Copy and customize
   cp frontend/.env.example frontend/.env.local
   ```

3. **Configure Google Cloud Credentials**
   - Create a service account in Google Cloud Console
   - Download the JSON key file
   - Place it in `backend/credentials/service-account.json`
   - Update `GOOGLE_APPLICATION_CREDENTIALS` in backend `.env`

### Installation

#### Option 1: Docker (Recommended)

```bash
# Start all services
docker-compose up -d

# Check services are running
docker-compose ps

# View logs
docker-compose logs -f
```

The application will be available at:

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Database: localhost:5432

#### Option 2: Local Development

**Backend Setup:**

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend Setup:**

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

**Database Setup:**

```bash
# Create database (if not using Docker)
createdb notebooklm_rag

# Initialize with schema
psql -d notebooklm_rag -f database/init.sql
```

## � Project Structure

```
notebooklm/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── core/           # Core functionality
│   │   ├── database/       # Database models & config
│   │   ├── schemas/        # Pydantic schemas
│   │   └── services/       # Business logic
│   ├── alembic/            # Database migrations
│   ├── tests/              # Backend tests
│   └── requirements.txt    # Python dependencies
├── frontend/               # Next.js frontend
│   ├── src/
│   │   ├── app/           # App router pages
│   │   ├── components/    # React components
│   │   ├── lib/          # Utilities & API client
│   │   └── stores/       # Zustand stores
│   └── package.json      # Node dependencies
├── database/              # Database schema
├── docker-compose.yml     # Container orchestration
└── README.md             # This file
```

## 🔧 Configuration

### Backend Environment Variables

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/notebooklm_rag

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Google Cloud
GOOGLE_APPLICATION_CREDENTIALS=./credentials/service-account.json
GOOGLE_CLOUD_PROJECT=your-project-id

# Redis (for caching)
REDIS_URL=redis://localhost:6379

# Environment
ENVIRONMENT=development
LOG_LEVEL=INFO
```

### Frontend Environment Variables

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=NotebookLM RAG System
NEXTAUTH_SECRET=your-nextauth-secret
NEXTAUTH_URL=http://localhost:3000
```

## 🗄️ Database Schema

The system uses PostgreSQL with the following main tables:

- **users**: User accounts and authentication
- **documents**: Uploaded documents and metadata
- **queries**: Query history and results
- **audit_logs**: System audit trail

Key features:

- UUID primary keys
- Automatic timestamps
- Soft deletes
- Full-text search indexes
- Performance optimizations

## � Authentication

The system uses JWT-based authentication with:

- Access tokens (30 minutes)
- Refresh tokens (7 days)
- Role-based access control
- Password hashing with bcrypt

### API Endpoints

#### Authentication

- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/refresh` - Token refresh
- `POST /api/auth/logout` - User logout

#### Documents

- `POST /api/documents/upload` - Upload documents
- `GET /api/documents` - List user documents
- `GET /api/documents/{id}` - Get document details
- `DELETE /api/documents/{id}` - Delete document

#### Queries

- `POST /api/queries` - Execute RAG query
- `GET /api/queries` - Get query history
- `GET /api/queries/{id}` - Get query details

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest tests/ -v
```

### Frontend Tests

```bash
cd frontend
npm test
```

### API Testing

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test with API documentation
open http://localhost:8000/docs
```

## 📊 Monitoring & Logging

The system includes comprehensive logging and monitoring:

- **Structured Logging**: JSON logs with correlation IDs
- **Performance Metrics**: Response times and error rates
- **Audit Trail**: User actions and system events
- **Health Checks**: Service health monitoring

### Log Files

- Backend: `backend/logs/app.log`
- Database: Container logs via `docker-compose logs postgres`

## 🚀 Deployment

### Production Deployment

1. **Update Environment Variables**

   ```env
   ENVIRONMENT=production
   DATABASE_URL=postgresql://prod_user:password@prod_host:5432/prod_db
   ```

2. **Build Production Images**

   ```bash
   docker-compose -f docker-compose.prod.yml build
   ```

3. **Deploy with Docker Compose**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

### Cloud Deployment

The application is ready for deployment on:

- **Google Cloud Run** (serverless)
- **AWS ECS** (containers)
- **Azure Container Instances**
- **Kubernetes** (any provider)

## 🛠️ Development

### Adding New Features

1. **Backend Changes**

   - Add models in `app/database/models/`
   - Create schemas in `app/schemas/`
   - Implement endpoints in `app/api/`
   - Add business logic in `app/services/`

2. **Frontend Changes**

   - Add components in `src/components/`
   - Create pages in `src/app/`
   - Update API client in `src/lib/api.ts`
   - Manage state in `src/stores/`

3. **Database Changes**
   - Create migration: `alembic revision --autogenerate -m "description"`
   - Apply migration: `alembic upgrade head`

### Code Quality

```bash
# Backend formatting
black backend/
isort backend/

# Frontend formatting
npm run lint
npm run format

# Type checking
mypy backend/
npm run type-check
```

## 📚 API Documentation

Interactive API documentation is available at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Troubleshooting

### Common Issues

1. **Import Errors During Setup**

   - Run `pip install -r requirements.txt` and `npm install`
   - These errors are normal during initial scaffolding

2. **Database Connection Issues**

   - Ensure PostgreSQL is running
   - Check database URL in environment variables
   - Verify database exists

3. **Google Cloud API Issues**

   - Verify service account credentials
   - Check API is enabled in Google Cloud Console
   - Ensure proper IAM permissions

4. **Port Conflicts**
   - Change ports in docker-compose.yml if needed
   - Default ports: 3000 (frontend), 8000 (backend), 5432 (database)

### Getting Help

- Check the logs: `docker-compose logs`
- Review API documentation: http://localhost:8000/docs
- Ensure all environment variables are set correctly

## 🎯 Next Steps

1. Install dependencies and start the application
2. Configure Google Cloud credentials
3. Upload your first documents
4. Test the RAG functionality
5. Customize the frontend for your use case
6. Deploy to production environment

Happy coding! 🚀
