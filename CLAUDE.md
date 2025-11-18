# CLAUDE.md - AI Assistant Guide for AI Code Review Assistant

## Project Overview

**Current Status**: Planning/Design Phase - Implementation Not Started

This repository contains the blueprint for a **full-stack AI Code Review Assistant** designed to automate code review processes using AI (Claude), static analysis tools, and GitHub integration. The comprehensive README.md serves as the implementation roadmap.

### Purpose
Automatically analyze GitHub pull requests for:
- Security vulnerabilities (using Bandit)
- Code quality issues (using Pylint)
- Complexity metrics (using Radon)
- AI-powered contextual reviews (using Claude API)
- Generate actionable findings with severity categorization

---

## Architecture Overview

### Tech Stack

**Backend**
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Migrations**: Alembic
- **Authentication**: JWT tokens + GitHub OAuth
- **Analysis Tools**: Bandit, Pylint, Radon
- **AI Integration**: Anthropic Claude API
- **Server**: Uvicorn (ASGI)

**Frontend**
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **Component Library**: shadcn/ui (Radix UI)
- **State Management**: Zustand
- **Data Fetching**: TanStack Query (React Query)
- **Routing**: React Router v6
- **Code Highlighting**: react-syntax-highlighter
- **Charts**: Recharts

**Infrastructure**
- **Containerization**: Docker + Docker Compose
- **Database Hosting**: PostgreSQL (self-hosted or Neon/Supabase)
- **Backend Deployment**: Railway/Render
- **Frontend Deployment**: Vercel/Netlify

### System Architecture

```
┌─────────────────────────────────────────────────────────┐
│          Frontend (React + TypeScript + Vite)           │
│                  Port: 5173 (dev)                       │
│  Dashboard → Repos → PRs → Review Details → Analytics   │
└────────────────────┬────────────────────────────────────┘
                     │ REST API (CORS enabled)
                     │
┌────────────────────▼────────────────────────────────────┐
│           Backend (FastAPI + Python)                     │
│                  Port: 8000 (dev)                       │
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │  Auth    │  │ GitHub   │  │ Review   │             │
│  │  (JWT)   │  │ Webhooks │  │ Service  │             │
│  └──────────┘  └──────────┘  └──────────┘             │
│                                                          │
│  Analysis Pipeline (async):                             │
│  Security → Quality → Complexity → AI Review            │
└────────────────────┬────────────────────────────────────┘
                     │ SQLAlchemy ORM
                     │
┌────────────────────▼────────────────────────────────────┐
│              PostgreSQL Database                         │
│  users, repositories, pull_requests, reviews, findings  │
└─────────────────────────────────────────────────────────┘
```

---

## Project Structure (Planned)

```
AI-code-review-assistant/
├── backend/
│   ├── alembic/                     # Database migrations
│   │   ├── versions/
│   │   └── env.py
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                  # FastAPI application entry
│   │   ├── config.py                # Settings (env vars)
│   │   ├── database.py              # DB connection & session
│   │   │
│   │   ├── models/                  # SQLAlchemy models
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── repository.py
│   │   │   ├── pull_request.py
│   │   │   ├── review.py
│   │   │   └── finding.py
│   │   │
│   │   ├── schemas/                 # Pydantic schemas (API contracts)
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── repository.py
│   │   │   ├── review.py
│   │   │   └── finding.py
│   │   │
│   │   ├── api/                     # API route handlers
│   │   │   ├── __init__.py
│   │   │   ├── auth.py              # /api/auth/*
│   │   │   ├── repositories.py      # /api/repositories/*
│   │   │   ├── pull_requests.py     # /api/pulls/*
│   │   │   ├── reviews.py           # /api/reviews/*
│   │   │   └── webhooks.py          # /api/webhooks/github
│   │   │
│   │   ├── services/                # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── github_service.py    # GitHub API interactions
│   │   │   ├── review_service.py    # Main review orchestration
│   │   │   └── analysis/
│   │   │       ├── __init__.py
│   │   │       ├── security.py      # Bandit integration
│   │   │       ├── quality.py       # Pylint integration
│   │   │       ├── complexity.py    # Radon integration
│   │   │       └── ai_reviewer.py   # Claude API integration
│   │   │
│   │   ├── core/                    # Core utilities
│   │   │   ├── __init__.py
│   │   │   ├── security.py          # JWT, password hashing
│   │   │   └── dependencies.py      # FastAPI dependencies
│   │   │
│   │   └── utils/
│   │       ├── __init__.py
│   │       └── git_parser.py        # Parse git diffs
│   │
│   ├── tests/                       # Backend tests
│   │   ├── __init__.py
│   │   ├── test_api/
│   │   └── test_services/
│   │
│   ├── requirements.txt             # Python dependencies
│   ├── .env.example                 # Environment template
│   └── alembic.ini                  # Alembic config
│
├── frontend/
│   ├── public/                      # Static assets
│   ├── src/
│   │   ├── components/
│   │   │   ├── ui/                  # shadcn components
│   │   │   │   ├── button.tsx
│   │   │   │   ├── card.tsx
│   │   │   │   ├── badge.tsx
│   │   │   │   └── ...
│   │   │   │
│   │   │   ├── layout/
│   │   │   │   ├── Navbar.tsx
│   │   │   │   └── Sidebar.tsx
│   │   │   │
│   │   │   ├── code/
│   │   │   │   ├── CodeViewer.tsx
│   │   │   │   └── DiffViewer.tsx
│   │   │   │
│   │   │   ├── review/
│   │   │   │   ├── FindingCard.tsx
│   │   │   │   ├── ReviewSummary.tsx
│   │   │   │   └── SeverityBadge.tsx
│   │   │   │
│   │   │   └── dashboard/
│   │   │       ├── StatsCard.tsx
│   │   │       └── MetricsChart.tsx
│   │   │
│   │   ├── pages/
│   │   │   ├── Login.tsx
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Repositories.tsx
│   │   │   ├── PullRequests.tsx
│   │   │   └── ReviewDetail.tsx
│   │   │
│   │   ├── lib/
│   │   │   ├── api.ts               # Axios instance + interceptors
│   │   │   ├── auth.ts              # Auth utilities
│   │   │   └── utils.ts             # Helper functions
│   │   │
│   │   ├── hooks/
│   │   │   ├── useAuth.ts
│   │   │   ├── useReviews.ts
│   │   │   └── useRepositories.ts
│   │   │
│   │   ├── store/
│   │   │   └── authStore.ts         # Zustand auth store
│   │   │
│   │   ├── types/
│   │   │   └── index.ts             # TypeScript types
│   │   │
│   │   ├── App.tsx                  # Main app component
│   │   ├── main.tsx                 # Entry point
│   │   └── index.css                # Global styles + Tailwind
│   │
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   └── .env.example
│
├── docker-compose.yml               # Multi-container setup
├── .gitignore
├── README.md                        # Project documentation
└── CLAUDE.md                        # This file (AI assistant guide)
```

---

## Database Schema

### Tables

**users**
- Stores GitHub user information
- Links to repositories via one-to-many relationship
- Contains OAuth access token (encrypted)

**repositories**
- User's GitHub repositories enabled for review
- Tracks webhook configuration
- One-to-many with pull_requests

**pull_requests**
- PR metadata from GitHub
- Tracks state (open/closed/merged)
- One-to-many with reviews

**reviews**
- Stores review execution results
- Status tracking (pending/in_progress/completed/failed)
- Overall score (0-100) and finding counts
- One-to-many with findings

**findings**
- Individual issues discovered during review
- Categorized by severity (critical/warning/info)
- Links to specific file/line number
- Tracks which tool found the issue

**review_metrics**
- Aggregated analytics data
- Time-series metrics for dashboard charts

See README.md lines 200-299 for complete SQL schema with indexes.

---

## API Endpoints

### Authentication (`/api/auth`)
- `POST /api/auth/github` - GitHub OAuth callback
- `POST /api/auth/token` - Exchange credentials for JWT
- `GET /api/auth/me` - Get current authenticated user

### Repositories (`/api/repositories`)
- `GET /api/repositories` - List user's repositories
- `POST /api/repositories` - Add repository for monitoring
- `DELETE /api/repositories/{id}` - Remove repository
- `POST /api/repositories/{id}/sync` - Manual sync with GitHub

### Pull Requests (`/api/pulls`)
- `GET /api/repositories/{id}/pulls` - List PRs for a repo
- `GET /api/pulls/{id}` - Get PR details
- `POST /api/pulls/{id}/review` - Trigger manual review

### Reviews (`/api/reviews`)
- `GET /api/reviews` - List all reviews
- `GET /api/reviews/{id}` - Get review details
- `GET /api/reviews/{id}/findings` - Get findings for a review

### Webhooks (`/api/webhooks`)
- `POST /api/webhooks/github` - GitHub webhook handler (PR events)

### Analytics (`/api/analytics`)
- `GET /api/analytics/dashboard` - Dashboard statistics
- `GET /api/analytics/trends` - Time-series data

---

## Development Workflow

### Initial Setup

1. **Clone and Navigate**
   ```bash
   git clone <repo-url>
   cd AI-code-review-assistant
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt

   # Copy and configure environment
   cp .env.example .env
   # Edit .env with actual values (DB connection, API keys)

   # Start PostgreSQL
   docker-compose up -d postgres

   # Run migrations
   alembic upgrade head

   # Start server
   uvicorn app.main:app --reload --port 8000
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install

   # Copy and configure environment
   cp .env.example .env
   # Edit .env with API URL

   # Start dev server
   npm run dev
   ```

4. **Full Stack with Docker**
   ```bash
   docker-compose up --build
   ```

### Environment Variables

**Backend (.env)**
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/code_reviewer

# Security
SECRET_KEY=<generate-random-key>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# GitHub
GITHUB_CLIENT_ID=<your-github-app-id>
GITHUB_CLIENT_SECRET=<your-github-app-secret>
GITHUB_WEBHOOK_SECRET=<webhook-secret>

# Claude API
ANTHROPIC_API_KEY=<your-api-key>

# CORS
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

**Frontend (.env)**
```bash
VITE_API_BASE_URL=http://localhost:8000
VITE_GITHUB_CLIENT_ID=<your-github-app-id>
```

---

## Key Implementation Patterns

### Backend Patterns

**1. Dependency Injection**
```python
# app/core/dependencies.py
from sqlalchemy.orm import Session

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Usage in routes
@router.get("/reviews")
def list_reviews(db: Session = Depends(get_db)):
    return db.query(Review).all()
```

**2. Async Analysis Pipeline**
```python
# app/services/review_service.py
async def analyze_pull_request(pr_id: str):
    # Run analyses in parallel for speed
    results = await asyncio.gather(
        security.analyze(pr),
        quality.analyze(pr),
        ai_reviewer.analyze(pr)
    )
    # Combine and store findings
```

**3. Pydantic Schemas for Validation**
```python
# app/schemas/review.py
class ReviewCreate(BaseModel):
    pull_request_id: str

class ReviewResponse(BaseModel):
    id: str
    status: str
    overall_score: int
    critical_count: int

    class Config:
        from_attributes = True  # Allows SQLAlchemy model conversion
```

**4. Error Handling**
```python
from fastapi import HTTPException

@router.get("/reviews/{review_id}")
def get_review(review_id: str, db: Session = Depends(get_db)):
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return review
```

### Frontend Patterns

**1. React Query for Data Fetching**
```typescript
// src/hooks/useReviews.ts
export function useReview(id: string) {
  return useQuery({
    queryKey: ['review', id],
    queryFn: () => api.get(`/reviews/${id}`).then(res => res.data),
    staleTime: 5000
  });
}
```

**2. Component Composition**
```typescript
// src/pages/ReviewDetail.tsx
export function ReviewDetail() {
  const { id } = useParams();
  const { data: review, isLoading } = useReview(id);

  if (isLoading) return <LoadingSpinner />;

  return (
    <div>
      <ReviewSummary review={review} />
      <FindingsList reviewId={id} />
    </div>
  );
}
```

**3. Zustand for Auth State**
```typescript
// src/store/authStore.ts
export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: localStorage.getItem('token'),
  login: (token, user) => {
    localStorage.setItem('token', token);
    set({ token, user });
  },
  logout: () => {
    localStorage.removeItem('token');
    set({ token: null, user: null });
  }
}));
```

**4. TypeScript Types**
```typescript
// src/types/index.ts
export interface Review {
  id: string;
  pull_request_id: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  overall_score: number;
  critical_count: number;
  warning_count: number;
  info_count: number;
  summary: string;
  created_at: string;
}

export interface Finding {
  id: string;
  review_id: string;
  category: string;
  severity: 'critical' | 'warning' | 'info';
  title: string;
  description: string;
  file_path: string;
  line_number: number;
  code_snippet: string;
  suggestion: string;
  tool_source: string;
}
```

---

## Code Conventions

### Python (Backend)

**Style Guide**: PEP 8
- Use snake_case for functions and variables
- Use PascalCase for classes
- Max line length: 88 characters (Black formatter)
- Use type hints for function signatures

**Example**:
```python
from typing import Optional, List
from sqlalchemy.orm import Session

def get_reviews_by_repo(
    db: Session,
    repo_id: str,
    status: Optional[str] = None,
    limit: int = 50
) -> List[Review]:
    """
    Retrieve reviews for a specific repository.

    Args:
        db: Database session
        repo_id: Repository UUID
        status: Optional status filter
        limit: Maximum number of results

    Returns:
        List of Review objects
    """
    query = db.query(Review).join(PullRequest).filter(
        PullRequest.repository_id == repo_id
    )

    if status:
        query = query.filter(Review.status == status)

    return query.limit(limit).all()
```

**Imports Order**:
1. Standard library
2. Third-party packages
3. Local application imports

### TypeScript (Frontend)

**Style Guide**: Airbnb TypeScript
- Use camelCase for functions and variables
- Use PascalCase for components and types
- Prefer functional components with hooks
- Use explicit return types for functions

**Example**:
```typescript
import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';
import type { Review } from '@/types';

interface ReviewListProps {
  repositoryId: string;
  status?: string;
}

export function ReviewList({ repositoryId, status }: ReviewListProps): JSX.Element {
  const { data: reviews, isLoading, error } = useQuery<Review[]>({
    queryKey: ['reviews', repositoryId, status],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (status) params.append('status', status);

      const response = await api.get(`/repositories/${repositoryId}/reviews`, { params });
      return response.data;
    }
  });

  if (isLoading) return <LoadingSpinner />;
  if (error) return <ErrorMessage error={error} />;

  return (
    <div className="space-y-4">
      {reviews?.map((review) => (
        <ReviewCard key={review.id} review={review} />
      ))}
    </div>
  );
}
```

### Git Commit Messages

Format: `<type>(<scope>): <subject>`

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Formatting, missing semicolons, etc.
- `refactor`: Code change that neither fixes a bug nor adds a feature
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples**:
```
feat(backend): implement GitHub webhook handler
fix(frontend): resolve infinite loop in useReviews hook
docs(readme): add deployment instructions
refactor(services): extract common analysis logic
test(api): add integration tests for review endpoints
```

---

## Testing Strategy

### Backend Testing

**Framework**: pytest

```python
# tests/test_api/test_reviews.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_review():
    response = client.post(
        "/api/reviews",
        json={"pull_request_id": "test-pr-id"},
        headers={"Authorization": "Bearer <token>"}
    )
    assert response.status_code == 201
    assert response.json()["status"] == "pending"

def test_get_review_not_found():
    response = client.get("/api/reviews/nonexistent")
    assert response.status_code == 404
```

**Run Tests**:
```bash
cd backend
pytest tests/ -v
pytest tests/ --cov=app  # With coverage
```

### Frontend Testing

**Framework**: Vitest + React Testing Library

```typescript
// src/components/review/__tests__/FindingCard.test.tsx
import { render, screen } from '@testing-library/react';
import { FindingCard } from '../FindingCard';

describe('FindingCard', () => {
  it('renders critical finding with correct styling', () => {
    const finding = {
      severity: 'critical',
      title: 'Security vulnerability',
      description: 'SQL injection risk',
      file_path: 'app/db.py',
      line_number: 42
    };

    render(<FindingCard finding={finding} />);

    expect(screen.getByText('Security vulnerability')).toBeInTheDocument();
    expect(screen.getByText(/app\/db.py:42/)).toBeInTheDocument();
  });
});
```

**Run Tests**:
```bash
cd frontend
npm test
npm run test:coverage
```

---

## Deployment Guide

### Docker Compose (Recommended for Development)

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: code_reviewer
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://postgres:postgres@postgres:5432/code_reviewer
    depends_on:
      - postgres
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000

  frontend:
    build: ./frontend
    ports:
      - "5173:5173"
    environment:
      VITE_API_BASE_URL: http://localhost:8000
    command: npm run dev -- --host

volumes:
  postgres_data:
```

### Production Deployment

**Backend (Railway/Render)**
1. Connect GitHub repository
2. Set environment variables
3. Deploy from `backend/` directory
4. Run migrations: `alembic upgrade head`

**Frontend (Vercel/Netlify)**
1. Connect GitHub repository
2. Set build command: `npm run build`
3. Set publish directory: `dist`
4. Set environment variables

**Database (Neon/Supabase)**
1. Create PostgreSQL database
2. Copy connection string to backend `.env`

---

## AI Assistant Guidelines

### When Implementing Features

1. **Always Read the README First**: The README.md contains the complete blueprint, database schema, and architecture decisions.

2. **Follow the Planned Structure**: Adhere to the directory structure outlined above. Don't create arbitrary new directories.

3. **Database Changes**:
   - Create Alembic migrations for schema changes
   - Never modify the database directly
   - Keep migrations reversible

4. **API Development**:
   - Use Pydantic schemas for request/response validation
   - Include proper error handling with HTTPException
   - Add docstrings to all route handlers
   - Maintain RESTful conventions

5. **Frontend Development**:
   - Use TypeScript for type safety
   - Leverage React Query for server state
   - Keep components small and focused
   - Use shadcn/ui components for consistency

6. **Security Considerations**:
   - Never commit secrets or API keys
   - Validate all user input
   - Use parameterized queries (SQLAlchemy handles this)
   - Implement proper CORS configuration
   - Store passwords with bcrypt hashing

7. **Testing Requirements**:
   - Write tests for new features
   - Ensure tests pass before committing
   - Aim for >80% code coverage on critical paths

### When Debugging

1. **Check Logs**: FastAPI logs are in console, browser network tab for frontend
2. **Database State**: Use `psql` or database GUI to inspect data
3. **API Testing**: Use curl, Postman, or FastAPI's `/docs` endpoint (Swagger UI)
4. **Common Issues**:
   - CORS errors: Check `ALLOWED_ORIGINS` in backend config
   - 404 on API calls: Verify frontend `VITE_API_BASE_URL`
   - Database connection: Check `DATABASE_URL` format
   - Token errors: Verify JWT secret consistency

### When Adding New Analysis Tools

1. Create new module in `backend/app/services/analysis/`
2. Follow the pattern:
   ```python
   async def analyze(pr: PullRequest) -> List[Finding]:
       """Run analysis and return findings."""
       findings = []
       # Run tool
       # Parse output
       # Convert to Finding objects
       return findings
   ```
3. Integrate in `review_service.py` pipeline
4. Update database if new finding categories are needed

### Communication Expectations

- **Ask Before Major Changes**: If deviating from the README architecture, explain why
- **Provide Context**: When suggesting alternatives, explain trade-offs
- **Code Snippets**: Show working examples when explaining concepts
- **Documentation**: Update CLAUDE.md if adding new patterns or conventions

---

## Common Tasks Reference

### Add a New API Endpoint

1. Create Pydantic schemas in `backend/app/schemas/`
2. Add route handler in appropriate `backend/app/api/` file
3. Implement business logic in `backend/app/services/`
4. Update frontend API client in `frontend/src/lib/api.ts`
5. Create React Query hook in `frontend/src/hooks/`
6. Write tests for both backend and frontend

### Add a New UI Component

1. Create component in appropriate `frontend/src/components/` subdirectory
2. Define TypeScript interfaces for props
3. Use shadcn/ui primitives where possible
4. Add to relevant page or parent component
5. Write tests in `__tests__` subdirectory

### Create Database Migration

```bash
cd backend
alembic revision --autogenerate -m "description of changes"
# Review generated migration
alembic upgrade head
```

### Add New Analysis Tool

1. Install tool: Add to `backend/requirements.txt`
2. Create analyzer: `backend/app/services/analysis/new_tool.py`
3. Integrate in pipeline: Update `review_service.py`
4. Add tests: `backend/tests/test_services/test_new_tool.py`

---

## Performance Considerations

1. **Database Indexing**: Indexes exist on common query patterns (see README.md lines 294-298)
2. **Async Operations**: Use `async/await` for I/O-bound operations (API calls, file I/O)
3. **Query Optimization**: Use `select_related`/`joinedload` to prevent N+1 queries
4. **Frontend Optimizations**:
   - React Query caching reduces redundant API calls
   - Code splitting with lazy loading for routes
   - Memoization for expensive calculations

---

## Security Best Practices

1. **Authentication**:
   - JWT tokens with expiration
   - Secure password hashing (bcrypt)
   - GitHub OAuth for user authentication

2. **Authorization**:
   - Verify user owns repository before access
   - Check permissions on all mutations
   - Validate webhook signatures from GitHub

3. **Data Protection**:
   - Store secrets in environment variables
   - Encrypt sensitive data at rest
   - Use HTTPS in production
   - Sanitize all user input

4. **API Security**:
   - Rate limiting on endpoints
   - CORS configured for specific origins
   - Request validation with Pydantic
   - SQL injection prevention (SQLAlchemy ORM)

---

## Resources

### Documentation
- **FastAPI**: https://fastapi.tiangolo.com/
- **React**: https://react.dev/
- **SQLAlchemy**: https://docs.sqlalchemy.org/
- **shadcn/ui**: https://ui.shadcn.com/
- **TanStack Query**: https://tanstack.com/query/

### Tools
- **Database GUI**: pgAdmin, DBeaver, TablePlus
- **API Testing**: Postman, Insomnia, HTTPie
- **Code Quality**: Black, Pylint, ESLint, Prettier

### GitHub Integration
- **GitHub Apps**: https://docs.github.com/en/developers/apps
- **Webhooks**: https://docs.github.com/en/developers/webhooks-and-events
- **API**: https://docs.github.com/en/rest

---

## Troubleshooting

### Backend Won't Start
- Check PostgreSQL is running: `docker ps`
- Verify DATABASE_URL in `.env`
- Check port 8000 is available: `lsof -i :8000`
- Run migrations: `alembic upgrade head`

### Frontend Can't Connect to Backend
- Verify backend is running on port 8000
- Check `VITE_API_BASE_URL` in frontend `.env`
- Inspect CORS settings in `backend/app/main.py`
- Check browser console for specific errors

### GitHub Webhook Not Triggering
- Verify webhook URL is publicly accessible (use ngrok for local dev)
- Check webhook secret matches `GITHUB_WEBHOOK_SECRET`
- Review GitHub webhook delivery logs
- Ensure webhook is configured for PR events

### Database Migration Errors
- Roll back: `alembic downgrade -1`
- Check for conflicting migrations
- Ensure database schema matches models
- Review migration file for SQL errors

---

## Future Enhancements (Nice-to-Have)

Based on README.md "Cut These If Behind Schedule" section:
- Advanced filtering/search with full-text search
- Real-time updates via WebSockets
- Multiple language support (expand beyond Python)
- Advanced analytics charts with drill-down
- User preferences and customization
- Export functionality (PDF reports, CSV exports)
- Slack/Discord notifications
- Custom rule configuration
- Team collaboration features
- CI/CD pipeline integration beyond GitHub

---

## Conclusion

This CLAUDE.md serves as your comprehensive guide to understanding and working with the AI Code Review Assistant project. Always refer back to README.md for the full implementation roadmap and detailed technical specifications.

**Key Principles**:
- Follow the established architecture
- Write clean, tested, documented code
- Prioritize security and performance
- Communicate clearly about changes
- Keep the user experience smooth

When in doubt, ask for clarification rather than making assumptions. Happy coding!
