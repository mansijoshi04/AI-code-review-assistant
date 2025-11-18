# Setup Instructions - AI Code Review Assistant

This guide will help you set up the development environment for the AI Code Review Assistant project.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.10+**
- **Node.js 18+** and npm
- **Docker** and Docker Compose
- **Git**
- **PostgreSQL** (optional, Docker will handle this)

## Project Structure

```
AI-code-review-assistant/
├── backend/          # FastAPI Python backend
├── frontend/         # React TypeScript frontend
├── docker-compose.yml
├── IMPLEMENTATION_PLAN.md
└── README.md
```

---

## Backend Setup

### 1. Navigate to Backend Directory

```bash
cd backend
```

### 2. Create Python Virtual Environment

```bash
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

```bash
cp .env.example .env
```

Edit the `.env` file and update the following values:
- `SECRET_KEY`: Generate a secure random key
- `GITHUB_CLIENT_ID`: Your GitHub OAuth App Client ID (Sprint 2)
- `GITHUB_CLIENT_SECRET`: Your GitHub OAuth App Secret (Sprint 2)
- `ANTHROPIC_API_KEY`: Your Claude API key (Sprint 4)

### 5. Start PostgreSQL Database

From the **root directory**, run:

```bash
docker-compose up -d postgres
```

This will start PostgreSQL on port 5432.

### 6. Run Database Migrations

```bash
# Initialize Alembic (only needed once, already done)
# alembic init alembic

# Run migrations (Sprint 1 will add actual tables)
alembic upgrade head
```

### 7. Start Backend Server

```bash
# From backend/ directory
uvicorn app.main:app --reload --port 8000

# Or using Python directly:
python -m app.main
```

The API will be available at:
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## Frontend Setup

### 1. Navigate to Frontend Directory

```bash
cd frontend
```

### 2. Install Node Dependencies

```bash
npm install
```

This will install all dependencies from `package.json`.

### 3. Set Up Environment Variables

```bash
cp .env.example .env
```

The default values should work for local development:
```
VITE_API_BASE_URL=http://localhost:8000
```

### 4. Start Frontend Dev Server

```bash
npm run dev
```

The frontend will be available at:
- **Frontend**: http://localhost:5173

---

## Verify Setup

### 1. Check Backend

Open your browser and visit:
- http://localhost:8000 - Should show API info
- http://localhost:8000/docs - Should show Swagger UI

### 2. Check Frontend

Open your browser and visit:
- http://localhost:5173 - Should show the React app

### 3. Check Database

```bash
# Connect to PostgreSQL
docker exec -it code-reviewer-db psql -U postgres -d code_reviewer

# List tables (will be empty in Sprint 0)
\dt

# Exit
\q
```

---

## Common Commands

### Backend

```bash
# Start backend server (with auto-reload)
uvicorn app.main:app --reload

# Run tests
pytest

# Run tests with coverage
pytest --cov=app tests/

# Format code
black app/

# Lint code
pylint app/

# Create new migration
alembic revision --autogenerate -m "description"

# Run migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Frontend

```bash
# Start dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run linter
npm run lint

# Type check
npm run type-check
```

### Docker

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f

# Start only database
docker-compose up -d postgres

# Remove all containers and volumes
docker-compose down -v
```

---

## Troubleshooting

### Backend Issues

**Problem**: `ModuleNotFoundError` when running backend
- **Solution**: Ensure virtual environment is activated and dependencies are installed

**Problem**: Database connection error
- **Solution**: Check if PostgreSQL is running: `docker ps`
- **Solution**: Verify DATABASE_URL in `.env`

**Problem**: Port 8000 already in use
- **Solution**: Kill the process using port 8000 or change the port in `config.py`

### Frontend Issues

**Problem**: `npm install` fails
- **Solution**: Delete `node_modules/` and `package-lock.json`, then run `npm install` again
- **Solution**: Try using Node 18 LTS

**Problem**: Vite build errors
- **Solution**: Clear Vite cache: `rm -rf node_modules/.vite`

**Problem**: API connection errors (CORS)
- **Solution**: Verify backend is running
- **Solution**: Check `ALLOWED_ORIGINS` in backend `.env`

### Database Issues

**Problem**: PostgreSQL container won't start
- **Solution**: Check if port 5432 is available
- **Solution**: Remove old volume: `docker-compose down -v`

**Problem**: Migration fails
- **Solution**: Check database connection
- **Solution**: Rollback and try again: `alembic downgrade -1`

---

## Development Workflow

1. **Start Docker services** (database):
   ```bash
   docker-compose up -d postgres
   ```

2. **Start backend** (in one terminal):
   ```bash
   cd backend
   source venv/bin/activate
   uvicorn app.main:app --reload
   ```

3. **Start frontend** (in another terminal):
   ```bash
   cd frontend
   npm run dev
   ```

4. **Make changes** and see them live-reload automatically

5. **Run tests** before committing:
   ```bash
   # Backend tests
   cd backend && pytest

   # Frontend lint
   cd frontend && npm run lint
   ```

---

## Next Steps

- ✅ **Sprint 0 Complete**: Development environment is set up
- 🔄 **Sprint 1**: Create database models and basic APIs
- 🔜 **Sprint 2**: Integrate GitHub OAuth and webhooks

See `IMPLEMENTATION_PLAN.md` for the complete roadmap.

---

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Vite Documentation](https://vitejs.dev/)
- [Tailwind CSS Documentation](https://tailwindcss.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)

---

## Getting Help

If you encounter issues:

1. Check the troubleshooting section above
2. Review the error messages carefully
3. Check the logs: `docker-compose logs -f` or console output
4. Refer to the official documentation
5. Open an issue on GitHub with details about the problem

Happy coding! 🚀
