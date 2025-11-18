# Sprint 1: Database Models Implementation

**Status**: ✅ **COMPLETE - Database Models Created**
**Date**: 2025-11-18
**Phase**: Backend Foundation - Database Layer

---

## Summary

Sprint 1 Phase 1 (Database Models) has been successfully completed. All SQLAlchemy models have been created with proper relationships, indexes, and constraints.

---

## Models Created

### 1. Base Model Utilities

**File**: `backend/app/models/base.py`

- `TimestampMixin` - Reusable mixin for created_at/updated_at fields
- Automatically handles timestamp management

### 2. User Model

**File**: `backend/app/models/user.py`

**Purpose**: Store GitHub user information and authentication data

**Fields**:
- `id` (UUID) - Primary key
- `github_id` (Integer) - Unique GitHub user ID
- `username` (String) - GitHub username
- `email` (String, nullable) - User email
- `avatar_url` (Text, nullable) - Profile picture URL
- `access_token` (Text, nullable) - GitHub OAuth access token
- `created_at`, `updated_at` (DateTime) - Timestamps

**Relationships**:
- `repositories` - One-to-many with Repository (cascade delete)

**Indexes**:
- `github_id` (unique index)
- `username` (index for search)

### 3. Repository Model

**File**: `backend/app/models/repository.py`

**Purpose**: Store GitHub repository information

**Fields**:
- `id` (UUID) - Primary key
- `user_id` (UUID) - Foreign key to users
- `github_id` (Integer) - Unique GitHub repository ID
- `name` (String) - Repository name
- `full_name` (String) - Full repository name (owner/repo)
- `owner` (String) - Repository owner
- `is_active` (Boolean) - Whether monitoring is active
- `webhook_id` (Integer, nullable) - GitHub webhook ID
- `created_at`, `updated_at` (DateTime) - Timestamps

**Relationships**:
- `user` - Many-to-one with User
- `pull_requests` - One-to-many with PullRequest (cascade delete)
- `review_metrics` - One-to-many with ReviewMetrics (cascade delete)

**Indexes**:
- `user_id` (index for user queries)
- `github_id` (unique index)

### 4. PullRequest Model

**File**: `backend/app/models/pull_request.py`

**Purpose**: Store GitHub pull request metadata

**Fields**:
- `id` (UUID) - Primary key
- `repository_id` (UUID) - Foreign key to repositories
- `pr_number` (Integer) - PR number within repository
- `title` (Text) - PR title
- `description` (Text, nullable) - PR description
- `author` (String, nullable) - PR author username
- `state` (String, nullable) - PR state (open, closed, merged)
- `base_branch` (String, nullable) - Target branch
- `head_branch` (String, nullable) - Source branch
- `files_changed` (Integer, nullable) - Number of files changed
- `additions` (Integer, nullable) - Lines added
- `deletions` (Integer, nullable) - Lines deleted
- `github_url` (Text, nullable) - URL to GitHub PR
- `created_at`, `updated_at` (DateTime) - Timestamps

**Relationships**:
- `repository` - Many-to-one with Repository
- `reviews` - One-to-many with Review (cascade delete)

**Constraints**:
- Unique constraint on (repository_id, pr_number)

**Indexes**:
- `repository_id` (index for repository queries)

### 5. Review Model

**File**: `backend/app/models/review.py`

**Purpose**: Store code review execution results

**Fields**:
- `id` (UUID) - Primary key
- `pull_request_id` (UUID) - Foreign key to pull_requests
- `status` (String, nullable) - Review status (pending, in_progress, completed, failed)
- `overall_score` (Integer, nullable) - Overall score (0-100)
- `summary` (Text, nullable) - AI-generated summary
- `critical_count` (Integer, default 0) - Count of critical findings
- `warning_count` (Integer, default 0) - Count of warning findings
- `info_count` (Integer, default 0) - Count of info findings
- `started_at` (DateTime, nullable) - When review started
- `completed_at` (DateTime, nullable) - When review completed
- `created_at` (DateTime) - When review was created

**Relationships**:
- `pull_request` - Many-to-one with PullRequest
- `findings` - One-to-many with Finding (cascade delete)

**Indexes**:
- `pull_request_id` (index)
- `(pull_request_id, status)` (composite index for filtering)

### 6. Finding Model

**File**: `backend/app/models/finding.py`

**Purpose**: Store individual code review findings/issues

**Fields**:
- `id` (UUID) - Primary key
- `review_id` (UUID) - Foreign key to reviews
- `category` (String, nullable) - Finding category (security, quality, performance, style, ai_suggestion)
- `severity` (String, nullable) - Finding severity (critical, warning, info)
- `title` (String) - Finding title (max 500 chars)
- `description` (Text, nullable) - Detailed description
- `file_path` (String, nullable) - File path (max 1000 chars)
- `line_number` (Integer, nullable) - Line number in file
- `code_snippet` (Text, nullable) - Code snippet showing the issue
- `suggestion` (Text, nullable) - Suggested fix
- `tool_source` (String, nullable) - Tool that found the issue (bandit, pylint, claude, etc.)
- `created_at` (DateTime) - When finding was created

**Relationships**:
- `review` - Many-to-one with Review

**Indexes**:
- `review_id` (index)
- `severity` (index for filtering)
- `(review_id, severity)` (composite index for efficient queries)

### 7. ReviewMetrics Model

**File**: `backend/app/models/review_metrics.py`

**Purpose**: Store daily aggregated analytics data

**Fields**:
- `id` (UUID) - Primary key
- `repository_id` (UUID) - Foreign key to repositories
- `date` (Date) - Date for metrics
- `total_reviews` (Integer, default 0) - Total reviews that day
- `avg_score` (Numeric 5,2, nullable) - Average score (0-100)
- `total_findings` (Integer, default 0) - Total findings count
- `critical_findings` (Integer, default 0) - Critical findings count
- `avg_review_time_seconds` (Integer, nullable) - Average review duration
- `created_at` (DateTime) - When metrics were created

**Relationships**:
- `repository` - Many-to-one with Repository

**Constraints**:
- Unique constraint on (repository_id, date)

**Indexes**:
- `repository_id` (index)
- `date` (index for time-series queries)
- `(repository_id, date)` (composite index for efficient queries)

---

## Database Schema Diagram

```
┌─────────────┐
│    User     │
│─────────────│
│ id (PK)     │───┐
│ github_id   │   │
│ username    │   │
│ email       │   │
│ access_token│   │
└─────────────┘   │
                  │
                  │ 1:N
                  │
┌─────────────┐   │
│ Repository  │◄──┘
│─────────────│
│ id (PK)     │───┐
│ user_id (FK)│   │
│ github_id   │   │
│ full_name   │   │
│ is_active   │   │
│ webhook_id  │   │
└─────────────┘   │
      │           │
      │ 1:N       │ 1:N
      │           │
      ▼           │
┌─────────────┐   │
│PullRequest  │   │
│─────────────│   │
│ id (PK)     │   │
│ repo_id (FK)│   │
│ pr_number   │   │
│ title       │   │
│ state       │   │
│ author      │   │
└─────────────┘   │
      │           │
      │ 1:N       │
      │           │
      ▼           │
┌─────────────┐   │
│   Review    │   │
│─────────────│   │
│ id (PK)     │   │
│ pr_id (FK)  │   │
│ status      │   │
│ score       │   │
│ summary     │   │
│ *_count     │   │
└─────────────┘   │
      │           │
      │ 1:N       │
      │           │
      ▼           │
┌─────────────┐   │
│  Finding    │   │
│─────────────│   │
│ id (PK)     │   │
│ review_id FK│   │
│ severity    │   │
│ category    │   │
│ title       │   │
│ file_path   │   │
│ line_number │   │
│ suggestion  │   │
└─────────────┘   │
                  │
                  │ 1:N
                  │
┌─────────────┐   │
│ReviewMetrics│◄──┘
│─────────────│
│ id (PK)     │
│ repo_id (FK)│
│ date        │
│ total_revs  │
│ avg_score   │
│ total_finds │
└─────────────┘
```

---

## Database Migration

**File**: `backend/alembic/versions/001_create_initial_schema.py`

**Status**: Manual migration created (PostgreSQL not available in environment)

**Migration Includes**:
- All 6 tables with proper column types
- All foreign key constraints with CASCADE delete
- All unique constraints
- All indexes for query optimization
- Proper UUID generation for primary keys
- Proper default values

**To Run Migration** (when database is available):
```bash
cd backend
source venv/bin/activate
alembic upgrade head
```

---

## Model Features

### Common Patterns

1. **UUID Primary Keys**: All models use UUID for primary keys (better for distributed systems)
2. **Timestamps**: Most models inherit TimestampMixin for automatic timestamp management
3. **Cascade Deletes**: All relationships configured with CASCADE delete for data integrity
4. **Indexes**: Strategic indexes for common query patterns
5. **to_dict() Methods**: All models have serialization methods for API responses

### Relationship Configuration

```python
# Example: One-to-Many with cascade delete
repositories = relationship(
    "Repository",
    back_populates="user",
    cascade="all, delete-orphan",
    lazy="dynamic",
)
```

- `cascade="all, delete-orphan"` - Automatically delete child records
- `lazy="dynamic"` - Returns a query object instead of loading all records
- `back_populates` - Two-way relationship definition

### Type Safety

All models use proper SQLAlchemy types:
- `UUID(as_uuid=True)` - Native Python UUID objects
- `String(length)` - Variable-length strings with limits
- `Text` - Unlimited text fields
- `Integer`, `Boolean`, `DateTime`, `Date`, `Numeric` - Standard types

---

## Files Created

```
backend/app/models/
├── __init__.py           # Model exports
├── base.py               # TimestampMixin
├── user.py               # User model
├── repository.py         # Repository model
├── pull_request.py       # PullRequest model
├── review.py             # Review model
├── finding.py            # Finding model
└── review_metrics.py     # ReviewMetrics model

backend/alembic/
├── env.py                # Updated with model imports
└── versions/
    └── 001_create_initial_schema.py  # Manual migration
```

---

## Next Steps (Sprint 1 Phase 2)

1. **Authentication System** (Days 6-7)
   - Security utilities (JWT, password hashing)
   - Auth schemas (Pydantic)
   - Auth endpoints (/api/auth/*)

2. **Repository CRUD APIs** (Days 8-9)
   - Repository schemas (Pydantic)
   - Repository endpoints (/api/repositories/*)
   - Authorization checks

3. **Testing** (Day 10)
   - Unit tests for models
   - Integration tests for APIs
   - Test database fixtures

---

## How to Use These Models

### Creating a User

```python
from app.models import User
from app.database import SessionLocal

db = SessionLocal()

user = User(
    github_id=123456,
    username="johndoe",
    email="john@example.com",
    avatar_url="https://avatar.url",
)

db.add(user)
db.commit()
db.refresh(user)
```

### Querying with Relationships

```python
from app.models import User, Repository

# Get user with repositories
user = db.query(User).filter(User.github_id == 123456).first()

# Access repositories (lazy-loaded)
repos = user.repositories.all()

# Query with joins
repos = (
    db.query(Repository)
    .join(User)
    .filter(User.username == "johndoe")
    .all()
)
```

### Creating Related Records

```python
# Create repository for a user
repo = Repository(
    user_id=user.id,
    github_id=789012,
    name="my-repo",
    full_name="johndoe/my-repo",
    owner="johndoe",
)

db.add(repo)
db.commit()
```

---

## Testing Checklist

- ✅ All models created with proper fields
- ✅ All relationships configured correctly
- ✅ All indexes defined
- ✅ All constraints implemented
- ✅ Migration file created
- ✅ Models exported in __init__.py
- ✅ Alembic env.py updated
- ⏳ Unit tests (Sprint 1 Phase 2)
- ⏳ Integration tests (Sprint 1 Phase 2)

---

## Known Limitations

1. **PostgreSQL Required**: Migration created but not tested (no database in environment)
2. **Access Token Security**: Currently stored as plain text - needs encryption in production
3. **No Model Validation**: Business logic validation should be in Pydantic schemas
4. **No Soft Deletes**: All deletes are hard deletes (can add in future if needed)

---

## Conclusion

✅ **Sprint 1 Phase 1 (Database Models) Complete**

All 6 core models have been successfully implemented with:
- Proper relationships and constraints
- Strategic indexes for performance
- Type safety and validation
- Migration script ready for deployment

**Ready for**: Sprint 1 Phase 2 (Authentication & APIs)

---

**Created by**: Claude AI Assistant
**Date**: 2025-11-18
**Sprint**: 1 - Backend Foundation
