# AI Code Review Assistant - 48-Hour Full-Stack Version

**Alright, let's go FULL STACK!** This is ambitious but doable. We'll build something that looks professional and works end-to-end.

---

## 🎯 Revised Architecture - Full Stack in 48 Hours

```
┌─────────────────────────────────────────────────────────┐
│               Frontend (React + TypeScript)              │
│           Vite + Tailwind + shadcn/ui                   │
│                                                          │
│  Dashboard → PR List → Review Details → Analytics       │
└────────────────────┬────────────────────────────────────┘
                     │ REST API
                     │
┌────────────────────▼────────────────────────────────────┐
│              Backend (FastAPI + Python)                  │
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │  Auth    │  │ GitHub   │  │ Review   │             │
│  │  Routes  │  │ Webhook  │  │ Service  │             │
│  └──────────┘  └──────────┘  └──────────┘             │
│                                                          │
│  ┌──────────────────────────────────────────┐          │
│  │         Analysis Pipeline                 │          │
│  │  Security → Quality → AI Review           │          │
│  └──────────────────────────────────────────┘          │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│              PostgreSQL Database                         │
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │  users   │  │   prs    │  │ findings │             │
│  │  repos   │  │ reviews  │  │ metrics  │             │
│  └──────────┘  └──────────┘  └──────────┘             │
└─────────────────────────────────────────────────────────┘
```

---

## ⏰ 48-Hour Timeline (Full Stack Edition)

### **Hour 0-6: Foundation + Backend Core** ☕

**Setup (Hour 0-1)**
```bash
✓ Create monorepo structure
✓ Set up FastAPI project
✓ Set up React + Vite project
✓ Configure PostgreSQL (Docker)
✓ Install all dependencies
```

**Database Models (Hour 1-3)**
```bash
✓ Design database schema
✓ Create SQLAlchemy models
✓ Set up Alembic migrations
✓ Seed initial data
```

**API Foundation (Hour 3-6)**
```bash
✓ Basic CRUD endpoints
✓ GitHub webhook endpoint
✓ Authentication (JWT)
✓ CORS configuration
✓ Test with Postman/curl
```

**Key Takeaway #1**: *Start with data models - they're the foundation. If your database schema is solid, everything else builds cleanly on top. Changes later are expensive.*

---

### **Hour 6-12: Analysis Engine + GitHub Integration** 😴 (Sleep after!)

**GitHub Integration (Hour 6-9)**
```bash
✓ GitHub App/OAuth setup
✓ Webhook handler for PR events
✓ Fetch PR diff
✓ Parse and store in database
✓ Background job system (optional: use simple threading)
```

**Analysis Pipeline (Hour 9-12)**
```bash
✓ Security scanner integration
✓ Code quality checker
✓ AI review with Claude
✓ Store findings in database
✓ Calculate metrics
```

**Key Takeaway #2**: *Webhooks are async by nature. Design your system to handle events that arrive at any time. Learn about event-driven architecture.*

---

### **Hour 12-24: Frontend Foundation** ☕

**Project Setup (Hour 12-14)**
```bash
✓ Vite + React + TypeScript
✓ Tailwind CSS configuration
✓ Install shadcn/ui components
✓ Set up React Router
✓ API client with Axios
```

**Core Pages (Hour 14-20)**
```bash
✓ Login/Authentication page
✓ Dashboard with stats
✓ Repository list
✓ PR list with filters
✓ Review detail page
```

**Components (Hour 20-24)**
```bash
✓ Code viewer with syntax highlighting
✓ Finding cards (Critical/Warning/Info)
✓ Metrics charts (basic)
✓ Loading states and error handling
```

**Key Takeaway #3**: *Component-driven development with a design system (shadcn/ui) speeds up UI work dramatically. Reuse, don't rebuild.*

---

### **Hour 24-36: Integration + Polish** 😴 (Sleep after!)

**API Integration (Hour 24-28)**
```bash
✓ Connect frontend to backend
✓ Real-time data fetching
✓ Optimistic UI updates
✓ Error handling and retry logic
```

**Enhanced Features (Hour 28-32)**
```bash
✓ GitHub OAuth flow
✓ Real-time review status
✓ Inline code comments UI
✓ Filter and search
```

**Testing (Hour 32-36)**
```bash
✓ Test critical API endpoints
✓ Test main user flows
✓ Fix major bugs
✓ Performance optimization
```

**Key Takeaway #4**: *Integration is where things break. Budget time for debugging API contracts, CORS issues, and data flow problems.*

---

### **Hour 36-44: Deployment + Documentation**

**Deployment (Hour 36-40)**
```bash
✓ Docker Compose setup
✓ Environment configuration
✓ Deploy backend (Railway/Render)
✓ Deploy frontend (Vercel/Netlify)
✓ Database hosting (Neon/Supabase)
```

**Documentation (Hour 40-44)**
```bash
✓ Comprehensive README
✓ Architecture diagrams
✓ API documentation
✓ Setup instructions
✓ Screenshots and GIFs
```

**Key Takeaway #5**: *Modern deployment is surprisingly easy with the right tools. Learn Docker basics and platform-as-a-service offerings.*

---

### **Hour 44-48: Demo + Resume Prep**

```bash
✓ Record demo video (5-7 minutes)
✓ Create presentation slides
✓ Test deployed application
✓ Write resume bullet points
✓ LinkedIn post draft
```

---

## 📊 Database Schema

```sql
-- Users
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    github_id INTEGER UNIQUE NOT NULL,
    username VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    avatar_url TEXT,
    access_token TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Repositories
CREATE TABLE repositories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    github_id INTEGER UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    owner VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    webhook_id INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Pull Requests
CREATE TABLE pull_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    repository_id UUID REFERENCES repositories(id) ON DELETE CASCADE,
    pr_number INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    author VARCHAR(255),
    state VARCHAR(50), -- open, closed, merged
    base_branch VARCHAR(255),
    head_branch VARCHAR(255),
    files_changed INTEGER,
    additions INTEGER,
    deletions INTEGER,
    github_url TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(repository_id, pr_number)
);

-- Reviews
CREATE TABLE reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pull_request_id UUID REFERENCES pull_requests(id) ON DELETE CASCADE,
    status VARCHAR(50), -- pending, in_progress, completed, failed
    overall_score INTEGER, -- 0-100
    summary TEXT,
    critical_count INTEGER DEFAULT 0,
    warning_count INTEGER DEFAULT 0,
    info_count INTEGER DEFAULT 0,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Findings
CREATE TABLE findings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    review_id UUID REFERENCES reviews(id) ON DELETE CASCADE,
    category VARCHAR(50), -- security, quality, performance, style, ai_suggestion
    severity VARCHAR(20), -- critical, warning, info
    title VARCHAR(500) NOT NULL,
    description TEXT,
    file_path VARCHAR(1000),
    line_number INTEGER,
    code_snippet TEXT,
    suggestion TEXT,
    tool_source VARCHAR(100), -- bandit, pylint, claude, etc.
    created_at TIMESTAMP DEFAULT NOW()
);

-- Metrics (for analytics)
CREATE TABLE review_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    repository_id UUID REFERENCES repositories(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    total_reviews INTEGER DEFAULT 0,
    avg_score DECIMAL(5,2),
    total_findings INTEGER DEFAULT 0,
    critical_findings INTEGER DEFAULT 0,
    avg_review_time_seconds INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(repository_id, date)
);

-- Indexes for performance
CREATE INDEX idx_prs_repo_state ON pull_requests(repository_id, state);
CREATE INDEX idx_reviews_pr_status ON reviews(pull_request_id, status);
CREATE INDEX idx_findings_review_severity ON findings(review_id, severity);
CREATE INDEX idx_metrics_repo_date ON review_metrics(repository_id, date);
```

---

## 🛠️ Tech Stack

### **Backend**
```python
# requirements.txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
alembic==1.12.1
pydantic==2.5.0
pydantic-settings==2.1.0
python-jose[cryptography]==3.3.0  # JWT
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
httpx==0.25.2  # Async HTTP
PyGithub==2.1.1
anthropic==0.7.0
bandit==1.7.5
pylint==3.0.2
radon==6.0.1
python-dotenv==1.0.0
```

### **Frontend**
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "axios": "^1.6.2",
    "zustand": "^4.4.7",
    "@tanstack/react-query": "^5.12.2",
    "tailwindcss": "^3.3.6",
    "@radix-ui/react-*": "latest",
    "lucide-react": "^0.294.0",
    "recharts": "^2.10.3",
    "react-syntax-highlighter": "^15.5.0",
    "date-fns": "^2.30.0",
    "clsx": "^2.0.0",
    "tailwind-merge": "^2.1.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.43",
    "@types/react-dom": "^18.2.17",
    "@vitejs/plugin-react": "^4.2.1",
    "typescript": "^5.3.3",
    "vite": "^5.0.8"
  }
}
```

---

## 📁 Project Structure

```
ai-code-reviewer/
├── backend/
│   ├── alembic/                    # Database migrations
│   │   ├── versions/
│   │   └── env.py
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI app
│   │   ├── config.py               # Settings
│   │   ├── database.py             # DB connection
│   │   ├── models/                 # SQLAlchemy models
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── repository.py
│   │   │   ├── pull_request.py
│   │   │   ├── review.py
│   │   │   └── finding.py
│   │   ├── schemas/                # Pydantic schemas
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── review.py
│   │   │   └── finding.py
│   │   ├── api/                    # API routes
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── repositories.py
│   │   │   ├── pull_requests.py
│   │   │   ├── reviews.py
│   │   │   └── webhooks.py
│   │   ├── services/               # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── github_service.py
│   │   │   ├── review_service.py
│   │   │   └── analysis/
│   │   │       ├── security.py
│   │   │       ├── quality.py
│   │   │       ├── complexity.py
│   │   │       └── ai_reviewer.py
│   │   ├── core/                   # Core utilities
│   │   │   ├── __init__.py
│   │   │   ├── security.py
│   │   │   └── dependencies.py
│   │   └── utils/
│   │       ├── __init__.py
│   │       └── git_parser.py
│   ├── tests/
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ui/                 # shadcn components
│   │   │   ├── layout/
│   │   │   │   ├── Navbar.tsx
│   │   │   │   └── Sidebar.tsx
│   │   │   ├── code/
│   │   │   │   ├── CodeViewer.tsx
│   │   │   │   └── DiffViewer.tsx
│   │   │   ├── review/
│   │   │   │   ├── FindingCard.tsx
│   │   │   │   ├── ReviewSummary.tsx
│   │   │   │   └── SeverityBadge.tsx
│   │   │   └── dashboard/
│   │   │       ├── StatsCard.tsx
│   │   │       └── MetricsChart.tsx
│   │   ├── pages/
│   │   │   ├── Login.tsx
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Repositories.tsx
│   │   │   ├── PullRequests.tsx
│   │   │   └── ReviewDetail.tsx
│   │   ├── lib/
│   │   │   ├── api.ts             # Axios instance
│   │   │   ├── auth.ts            # Auth utilities
│   │   │   └── utils.ts
│   │   ├── hooks/
│   │   │   ├── useAuth.ts
│   │   │   ├── useReviews.ts
│   │   │   └── useRepositories.ts
│   │   ├── store/
│   │   │   └── authStore.ts       # Zustand store
│   │   ├── types/
│   │   │   └── index.ts
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── index.css
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── tailwind.config.js
│
├── docker-compose.yml
├── .gitignore
└── README.md
```

---

## 🎨 Key UI Pages & Features

### **1. Dashboard** (Landing page after login)
```
┌─────────────────────────────────────────────────────────┐
│  AI Code Reviewer                    [Profile] [Logout] │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  📊 Overview                                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ Total Reviews│  │Active Repos  │  │  Avg Score   │ │
│  │     247      │  │      8       │  │    8.5/10    │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│                                                          │
│  📈 Review Trends (Last 30 Days)                        │
│  ┌──────────────────────────────────────────────────┐  │
│  │     [Line Chart showing reviews over time]        │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  🔍 Recent Reviews                                      │
│  ┌──────────────────────────────────────────────────┐  │
│  │ 🟢 PR #123 - Add authentication   5 min ago      │  │
│  │ 🟡 PR #122 - Fix database bug    15 min ago      │  │
│  │ 🔴 PR #121 - Update dependencies  1 hour ago     │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### **2. Pull Requests List**
```
┌─────────────────────────────────────────────────────────┐
│  🔍 [Search PRs...]         [Filter: All▾] [Sort: Date▾]│
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │ PR #145 - Implement payment gateway              │  │
│  │ user/awesome-app  •  3 files  •  +234 -45       │  │
│  │ 🔴 Critical: 2  🟡 Warning: 5  💡 Info: 8       │  │
│  │ [View Review]                      2 hours ago   │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │ PR #144 - Fix authentication bug                 │  │
│  │ user/awesome-app  •  1 file  •  +12 -8          │  │
│  │ 🟢 All Clear!                                    │  │
│  │ [View Review]                      5 hours ago   │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### **3. Review Detail Page** (Most Important!)
```
┌─────────────────────────────────────────────────────────┐
│  ← Back to PRs                                          │
├─────────────────────────────────────────────────────────┤
│  PR #145: Implement payment gateway                     │
│  user/awesome-app                                       │
│  Branch: feature/payments → main                        │
│                                                          │
│  📊 Review Score: 7.2/10        Status: ✅ Completed    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ 🔴 Critical  │  │ 🟡 Warnings  │  │ 💡 Info      │ │
│  │      2       │  │      5       │  │      8       │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│                                                          │
│  📝 Summary                                             │
│  This PR introduces payment processing. Overall well-   │
│  structured, but contains security concerns in API      │
│  key handling and missing error handling...             │
│                                                          │
│  🔍 Findings                                            │
│  ┌──────────────────────────────────────────────────┐  │
│  │ 🔴 CRITICAL                                       │  │
│  │ Hardcoded API credentials                         │  │
│  │ payments/stripe.py:23                            │  │
│  │                                                   │  │
│  │ ``` python                                        │  │
│  │ API_KEY = "sk_live_abcd1234"  # ⚠️ Security risk!│  │
│  │ ```                                               │  │
│  │                                                   │  │
│  │ 💡 Suggestion: Use environment variables         │  │
│  │ Source: Bandit (B105)                            │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │ 🟡 WARNING                                        │  │
│  │ Missing error handling in API call               │  │
│  │ payments/api.py:45                               │  │
│  │ ...                                              │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start Commands

### **Backend Setup**
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Database
docker-compose up -d postgres
alembic upgrade head

# Run
uvicorn app.main:app --reload --port 8000
```

### **Frontend Setup**
```bash
cd frontend
npm install
npm run dev
# Runs on http://localhost:5173
```

### **Full Stack with Docker**
```bash
docker-compose up --build
```

---

## 🔑 Core API Endpoints

```python
# Authentication
POST   /api/auth/github              # GitHub OAuth callback
POST   /api/auth/token                # Get JWT token
GET    /api/auth/me                   # Get current user

# Repositories
GET    /api/repositories              # List user's repos
POST   /api/repositories              # Add repo for monitoring
DELETE /api/repositories/{id}         # Remove repo
POST   /api/repositories/{id}/sync    # Manual sync

# Pull Requests
GET    /api/repositories/{id}/pulls   # List PRs
GET    /api/pulls/{id}                # Get PR details
POST   /api/pulls/{id}/review         # Trigger manual review

# Reviews
GET    /api/reviews                   # List all reviews
GET    /api/reviews/{id}              # Get review details
GET    /api/reviews/{id}/findings     # Get review findings

# Webhooks
POST   /api/webhooks/github           # GitHub webhook handler

# Analytics
GET    /api/analytics/dashboard       # Dashboard stats
GET    /api/analytics/trends          # Time-series data
```

---

## 💡 Key Implementation Snippets

### **Backend: Main FastAPI App**

```python
# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, repositories, pull_requests, reviews, webhooks
from app.database import engine, Base

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Code Reviewer API",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(repositories.router, prefix="/api/repositories", tags=["repositories"])
app.include_router(pull_requests.router, prefix="/api/pulls", tags=["pull_requests"])
app.include_router(reviews.router, prefix="/api/reviews", tags=["reviews"])
app.include_router(webhooks.router, prefix="/api/webhooks", tags=["webhooks"])

@app.get("/")
def read_root():
    return {"message": "AI Code Reviewer API", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
```

### **Backend: Review Service (Core Logic)**

```python
# backend/app/services/review_service.py
from sqlalchemy.orm import Session
from app.models import Review, Finding, PullRequest
from app.services.analysis import security, quality, ai_reviewer
import asyncio

class ReviewService:
    def __init__(self, db: Session):
        self.db = db
    
    async def analyze_pull_request(self, pr_id: str) -> Review:
        """Main review orchestration"""
        # Get PR from database
        pr = self.db.query(PullRequest).filter(PullRequest.id == pr_id).first()
        
        # Create review record
        review = Review(
            pull_request_id=pr_id,
            status="in_progress"
        )
        self.db.add(review)
        self.db.commit()
        
        try:
            # Run analyses in parallel
            security_findings = await security.analyze(pr)
            quality_findings = await quality.analyze(pr)
            ai_findings = await ai_reviewer.analyze(pr)
            
            # Combine all findings
            all_findings = security_findings + quality_findings + ai_findings
            
            # Save findings to database
            for finding in all_findings:
                db_finding = Finding(
                    review_id=review.id,
                    **finding.dict()
                )
                self.db.add(db_finding)
            
            # Calculate score and summary
            review.overall_score = self._calculate_score(all_findings)
            review.critical_count = len([f for f in all_findings if f.severity == "critical"])
            review.warning_count = len([f for f in all_findings if f.severity == "warning"])
            review.info_count = len([f for f in all_findings if f.severity == "info"])
            review.summary = await ai_reviewer.generate_summary(all_findings)
            review.status = "completed"
            
            self.db.commit()
            return review
            
        except Exception as e:
            review.status = "failed"
            self.db.commit()
            raise e
    
    def _calculate_score(self, findings) -> int:
        """Calculate 0-100 score based on findings"""
        score = 100
        for finding in findings:
            if finding.severity == "critical":
                score -= 15
            elif finding.severity == "warning":
                score -= 5
            elif finding.severity == "info":
                score -= 1
        return max(0, score)
```

### **Frontend: Review Detail Page**

```typescript
// frontend/src/pages/ReviewDetail.tsx
import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { FindingCard } from '@/components/review/FindingCard';
import { ReviewSummary } from '@/components/review/ReviewSummary';
import { CodeViewer } from '@/components/code/CodeViewer';

export function ReviewDetail() {
  const { id } = useParams();
  
  const { data: review, isLoading } = useQuery({
    queryKey: ['review', id],
    queryFn: () => api.get(`/reviews/${id}`).then(res => res.data)
  });

  const { data: findings } = useQuery({
    queryKey: ['findings', id],
    queryFn: () => api.get(`/reviews/${id}/findings`).then(res => res.data)
  });

  if (isLoading) return <div>Loading...</div>;

  const criticalFindings = findings?.filter(f => f.severity === 'critical') || [];
  const warningFindings = findings?.filter(f => f.severity === 'warning') || [];
  const infoFindings = findings?.filter(f => f.severity === 'info') || [];

  return (
    <div className="container mx-auto p-6">
      <ReviewSummary review={review} />
      
      <div className="mt-8 space-y-4">
        <h2 className="text-2xl font-bold">Findings</h2>
        
        {criticalFindings.length > 0 && (
          <div>
            <h3 className="text-xl font-semibold text-red-600 mb-3">
              🔴 Critical Issues
            </h3>
            {criticalFindings.map(finding => (
              <FindingCard key={finding.id} finding={finding} />
            ))}
          </div>
        )}
        
        {warningFindings.length > 0 && (
          <div>
            <h3 className="text-xl font-semibold text-yellow-600 mb-3">
              🟡 Warnings
            </h3>
            {warningFindings.map(finding => (
              <FindingCard key={finding.id} finding={finding} />
            ))}
          </div>
        )}
        
        {infoFindings.length > 0 && (
          <div>
            <h3 className="text-xl font-semibold text-blue-600 mb-3">
              💡 Suggestions
            </h3>
            {infoFindings.map(finding => (
              <FindingCard key={finding.id} finding={finding} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
```

### **Frontend: Finding Card Component**

```typescript
// frontend/src/components/review/FindingCard.tsx
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

interface FindingCardProps {
  finding: {
    severity: 'critical' | 'warning' | 'info';
    title: string;
    description: string;
    file_path: string;
    line_number: number;
    code_snippet: string;
    suggestion: string;
    tool_source: string;
  };
}

export function FindingCard({ finding }: FindingCardProps) {
  const severityColors = {
    critical: 'bg-red-100 text-red-800 border-red-300',
    warning: 'bg-yellow-100 text-yellow-800 border-yellow-300',
    info: 'bg-blue-100 text-blue-800 border-blue-300',
  };

  return (
    <Card className={`mb-4 ${severityColors[finding.severity]}`}>
      <CardHeader>
        <div className="flex justify-between items-start">
          <CardTitle className="text-lg">{finding.title}</CardTitle>
          <Badge variant="outline">{finding.tool_source}</Badge>
        </div>
        <p className="text-sm text-gray-600">
          {finding.file_path}:{finding.line_number}
        </p>
      </CardHeader>
      <CardContent>
        <p className="mb-4">{finding.description}</p>
        
        {finding.code_snippet && (
          <div className="mb-4">
            <SyntaxHighlighter language="python" style={vscDarkPlus}>
              {finding.code_snippet}
            </SyntaxHighlighter>
          </div>
        )}
        
        {finding.suggestion && (
          <div className="bg-white p-3 rounded border-l-4 border-green-500">
            <p className="font-semibold text-sm mb-1">💡 Suggestion:</p>
            <p className="text-sm">{finding.suggestion}</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
```

---

## 🎯 Minimum Viable Features (Must Have)

### **Backend**
- [x] User authentication (GitHub OAuth)
- [x] Repository management (add/remove/list)
- [x] GitHub webhook handler
- [x] PR analysis pipeline
- [x] Store reviews and findings in database
- [x] API endpoints for frontend

### **Frontend**
- [x] Login page
- [x] Dashboard with statistics
- [x] Repository list
- [x] PR list with status
- [x] Review detail page with findings
- [x] Basic filtering and search

### **Analysis**
- [x] Security scanning (Bandit)
- [x] Code quality (Pylint)
- [x] AI review (Claude)
- [x] Severity categorization
- [x] Score calculation

---

## 🎬 Demo Script (5-7 minutes)

**Minute 0-1: Problem**
- Show typical PR review process
- "Code reviews take hours, miss subtle bugs"

**Minute 1-3: Solution Demo**
- Login to the app
- Show dashboard with repos
- Click on a PR
- Show real-time analysis
- Walk through findings (critical → warning → info)

**Minute 3-5: Technical Deep Dive**
- Quick architecture diagram
- Show database schema
- Show one component (AI review service)
- Highlight tech stack

**Minute 5-7: Results & Impact**
- Show metrics: X PRs reviewed, Y issues found
- Time savings calculation
- Future roadmap

---

## 📝 Resume Block (Draft)

```
AI Code Review Assistant | Python, React, PostgreSQL, Claude AI, FastAPI
• Architected full-stack code review automation platform with React/TypeScript 
  frontend, FastAPI backend, and PostgreSQL database, processing 100+ PRs with 
  real-time analysis and comprehensive reporting
• Integrated GitHub webhooks and OAuth for seamless CI/CD integration, enabling 
  automatic PR review triggers and inline comment posting via GitHub API
• Implemented multi-layered analysis pipeline combining static analysis tools 
  (Bandit, Pylint) with Claude AI for context-aware security, quality, and 
  architectural recommendations
• Designed scalable database schema with efficient indexing strategies, 
  supporting complex queries for analytics dashboard showing trends, metrics, 
  and historical review data
• Built modern React UI with shadcn/ui component library and TanStack Query 
  for optimistic updates, featuring syntax-highlighted code viewers and 
  severity-categorized finding cards
```

---

## ⚠️ 48-Hour Survival Strategy

### **Critical Path (Don't Skip)**
1. ✅ Database schema design (Hour 1-2)
2. ✅ Basic CRUD APIs (Hour 3-5)
3. ✅ GitHub webhook (Hour 6-8)
4. ✅ Analysis pipeline (Hour 9-12)
5. ✅ Frontend skeleton + routing (Hour 14-16)
6. ✅ Review detail page (Hour 18-22)
7. ✅ Integration testing (Hour 32-36)
8. ✅ Deployment (Hour 36-40)

### **Time Savers**
- **Use shadcn/ui**: Pre-built components save 10+ hours
- **Copy-paste SQL**: Don't type schema by hand
- **Docker Compose**: One command database setup
- **GitHub Copilot**: Let AI write boilerplate
- **Template repos**: Start with Vite/FastAPI templates

### **Cut These If Behind Schedule**
- ❌ Advanced filtering/search
- ❌ Real-time updates (polling is fine)
- ❌ Multiple language support
- ❌ Analytics charts (tables are enough)
- ❌ User settings/preferences
- ❌ Export features

---

## 🚀 Let's Build This!

**Your next 4 hours should look like:**

```bash
Hour 1: Setup
[ ] Create GitHub repo
[ ] Initialize FastAPI project (use template)
[ ] Initialize React project (Vite)
[ ] Set up Docker Compose with PostgreSQL
[ ] Get all API keys

Hour 2: Database
[ ] Write SQL schema
[ ] Create SQLAlchemy models
[ ] Run first migration
[ ] Test database connection

Hour 3: Core API
[ ] User model and auth endpoints
[ ] Repository CRUD endpoints
[ ] Test with curl/Postman
[ ] Set up CORS

Hour 4: GitHub Integration
[ ] GitHub OAuth flow
[ ] Webhook endpoint skeleton
[ ] Test receiving PR events
[ ] Git commit everything
