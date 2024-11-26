# AudioV4 Complete Implementation Guide

## Table of Contents
1. [Project Overview](#1-project-overview)
2. [Core Development Stack](#2-core-development-stack)
3. [Project Structure](#3-project-structure)
4. [Error Handling & Debugging](#4-error-handling--debugging)
5. [Database Schema](#5-database-schema)
6. [API Implementation](#6-api-implementation)
7. [Testing Framework](#7-testing-framework)
8. [AI Integration](#8-ai-integration)
9. [Development Workflow](#9-development-workflow)
10. [Deployment](#10-deployment)

## 1. Project Overview

### Purpose
AudioV4 is an AI-powered platform that:
- Creates and manages questionnaire templates
- Processes responses to generate book outlines
- Converts outlines to audiobooks using AI
- Provides comprehensive error tracking and testing

### System Architecture
```ascii
                                      ┌──────────────┐
                                      │   Supabase   │
                                      │  (Database)  │
                                      └──────┬───────┘
                                            │
┌──────────────┐    ┌──────────────┐    ┌──┴───────────┐    ┌──────────────┐
│  Templates   │    │ Questionnaire│    │    FastAPI    │    │   OpenAI     │
│  Management  │◄──►│  Responses   │◄──►│   Backend    │◄──►│  (AI & TTS)  │
└──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘
                                            │
                                      ┌─────┴──────┐
                                      │  Testing & │
                                      │ Monitoring │
                                      └────────────┘
```

## 2. Core Development Stack

### Main Dependencies
```toml
# pyproject.toml
[tool.poetry.dependencies]
python = "^3.11"
fastapi = "^0.104.1"
uvicorn = "^0.24.0"
supabase = "^1.0.3"
python-dotenv = "^1.0.0"
pydantic = "^2.4.2"
openai = "^1.2.3"
pytest = "^7.4.3"
pytest-asyncio = "^0.21.1"
httpx = "^0.25.1"
python-multipart = "^0.0.6"
pydub = "^0.25.1"
loguru = "^0.7.2"
sqlalchemy = "^2.0.23"
alembic = "^1.12.1"
```

### Environment Configuration
```env
# .env
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
OPENAI_API_KEY=your_openai_key
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG
```

## 3. Project Structure

```
audiov4/
├── alembic/
│   └── versions/
├── app/
│   ├── api/
│   │   ├── dependencies.py
│   │   ├── errors.py
│   │   └── routes/
│   │       ├── templates.py
│   │       ├── questionnaires.py
│   │       ├── outlines.py
│   │       └── audiobooks.py
│   ├── core/
│   │   ├── config.py
│   │   ├── logging.py
│   │   └── security.py
│   ├── db/
│   │   ├── base.py
│   │   └── session.py
│   ├── models/
│   │   ├── template.py
│   │   ├── questionnaire.py
│   │   ├── outline.py
│   │   └── audiobook.py
│   ├── schemas/
│   │   ├── template.py
│   │   ├── questionnaire.py
│   │   ├── outline.py
│   │   └── audiobook.py
│   ├── services/
│   │   ├── ai_service.py
│   │   ├── audio_service.py
│   │   └── storage_service.py
│   └── utils/
│       ├── ai_prompts.py
│       └── audio_processing.py
├── tests/
│   ├── conftest.py
│   ├── test_api/
│   ├── test_services/
│   └── test_utils/
├── alembic.ini
├── main.py
├── pyproject.toml
└── README.md
```

## 4. Error Handling & Debugging

### Core Error Handler
```python
# app/core/errors.py
from fastapi import HTTPException
from typing import Optional, Any, Dict
import traceback
import sys
import uuid
from loguru import logger

class DetailedHTTPException(HTTPException):
    def __init__(
        self,
        status_code: int,
        detail: str,
        internal_error: Optional[Exception] = None,
        context: Dict[str, Any] = None
    ):
        self.request_id = str(uuid.uuid4())
        self.internal_error = internal_error
        self.error_trace = None
        self.context = context or {}
        
        if internal_error:
            self.error_trace = {
                'request_id': self.request_id,
                'error_type': type(internal_error).__name__,
                'message': str(internal_error),
                'traceback': traceback.format_tb(internal_error.__traceback__),
                'sys_info': {
                    'python_version': sys.version,
                    'platform': sys.platform
                },
                'context': self.context
            }
            
            # Log detailed error information
            logger.error(
                f"Detailed error occurred: {detail}",
                error_trace=self.error_trace
            )
        
        super().__init__(status_code, detail)

# Middleware for request tracking
from fastapi import Request
from fastapi.responses import JSONResponse

@app.middleware("http")
async def request_handler(request: Request, call_next):
    request_id = str(uuid.uuid4())
    logger.bind(request_id=request_id)
    
    try:
        response = await call_next(request)
        return response
    except DetailedHTTPException as e:
        return JSONResponse(
            status_code=e.status_code,
            content={
                'status': 'error',
                'detail': e.detail,
                'request_id': e.request_id,
                'debug_info': e.error_trace if app.debug else None
            }
        )
    except Exception as e:
        logger.exception("Unhandled exception occurred")
        return JSONResponse(
            status_code=500,
            content={
                'status': 'error',
                'detail': 'Internal server error',
                'request_id': request_id,
                'debug_info': str(e) if app.debug else None
            }
        )
```

### Logging Configuration
```python
# app/core/logging.py
from loguru import logger
import sys
import json
from pathlib import Path

def setup_logging():
    # Remove default logger
    logger.remove()
    
    # Configure JSON logging
    log_format = {
        "time": "{time:YYYY-MM-DD HH:mm:ss.SSS}",
        "level": "{level}",
        "request_id": "{extra[request_id]}",
        "message": "{message}",
        "extra": "{extra}"
    }
    
    # Console handler for development
    logger.add(
        sys.stdout,
        format=lambda record: json.dumps(log_format),
        level="DEBUG" if app.debug else "INFO",
        serialize=True
    )
    
    # File handler for production
    log_path = Path("logs/audiov4.log")
    log_path.parent.mkdir(exist_ok=True)
    
    logger.add(
        log_path,
        rotation="500 MB",
        retention="10 days",
        format=lambda record: json.dumps(log_format),
        level="DEBUG",
        serialize=True
    )
    
    return logger
```

## 5. Database Schema

### Supabase Schema
```sql
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Templates table
CREATE TABLE templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT NOT NULL,
    description TEXT,
    sections JSONB NOT NULL,
    version INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Questionnaire responses
CREATE TABLE questionnaire_responses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    template_id UUID REFERENCES templates(id),
    responses JSONB NOT NULL,
    status TEXT NOT NULL DEFAULT 'submitted'
        CHECK (status IN ('draft', 'submitted', 'processing', 'completed')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Book outlines
CREATE TABLE book_outlines (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    questionnaire_id UUID REFERENCES questionnaire_responses(id),
    chapters JSONB NOT NULL,
    status TEXT NOT NULL DEFAULT 'draft'
        CHECK (status IN ('draft', 'approved', 'generating_audio')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Audiobooks
CREATE TABLE audiobooks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    outline_id UUID REFERENCES book_outlines(id),
    chapter_files JSONB NOT NULL,
    total_duration INTEGER,
    status TEXT NOT NULL DEFAULT 'generating'
        CHECK (status IN ('generating', 'completed', 'failed')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Triggers for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_templates_updated_at
    BEFORE UPDATE ON templates
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- (Similar triggers for other tables)
```

## 6. API Implementation

### Core FastAPI Setup
```python
# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import setup_logging

app = FastAPI(
    title="AudioV4 API",
    description="AI-powered audiobook generation platform",
    version="4.0.0",
    debug=settings.DEBUG
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup logging
logger = setup_logging()

# Import and include routers
from app.api.routes import templates, questionnaires, outlines, audiobooks

app.include_router(templates.router, prefix="/api/templates", tags=["templates"])
app.include_router(questionnaires.router, prefix="/api/questionnaires", tags=["questionnaires"])
app.include_router(outlines.router, prefix="/api/outlines", tags=["outlines"])
app.include_router(audiobooks.router, prefix="/api/audiobooks", tags=["audiobooks"])
```

### Template Routes Example
```python
# app/api/routes/templates.py
from fastapi import APIRouter, Depends
from app.schemas.template import TemplateCreate, TemplateResponse
from app.services.template_service import TemplateService
from typing import List
from app.core.errors import DetailedHTTPException

router = APIRouter()

@router.post("/", response_model=TemplateResponse)
async def create_template(
    template: TemplateCreate,
    service: TemplateService = Depends()
):
    try:
        return await service.create_template(template)
    except Exception as e:
        raise DetailedHTTPException(
            status_code=500,
            detail="Failed to create template",
            internal_error=e,
            context={'template_data': template.dict()}
        )

@router.get("/", response_model=List[TemplateResponse])
async def list_templates(
    service: TemplateService = Depends(),
    skip: int = 0,
    limit: int = 100
):
    try:
        return await service.list_templates(skip=skip, limit=limit)
    except Exception as e:
        raise DetailedHTTPException(
            status_code=500,
            detail="Failed to list templates",
            internal_error=e,
            context={'skip': skip, 'limit': limit}
        )
```

### Template Service Example
```python
# app/services/template_service.py
from app.schemas.template import TemplateCreate
from app.core.errors import DetailedHTTPException
from loguru import logger

class TemplateService:
    def __init__(self, supabase_client=Depends(get_supabase_client)):
        self.supabase = supabase_client
        
    async def create_template(self, template: TemplateCreate):
        try:
            response = self.supabase.table('templates').insert(
                template.dict()
            ).execute()
            
            if 'error' in response:
                raise DetailedHTTPException(
                    status_code=500,
                    detail="Database error while creating template",
                    internal_error=response['error']
                )
                
            return response.data[0]
        except Exception as e:
            logger.exception("Template creation failed")
            raise DetailedHTTPException(
                status_code=500,
                detail="Failed to create template",
                internal_error=e
            )
```

## 7. Testing Framework

### Test Configuration
```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
import os
from dotenv import load_dotenv

# Load test environment variables
load_dotenv('.env.test')

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def test_template():
    return {
        "title": "Test Template",
        "description": "Test Description",
        "sections": [
            {
                "title": "Section 1",
                "questions": [
                    {
                        "text": "Question 1",
                        "type": "text"
                    }
                ]
            }
        ]
    }
```

### API Tests
```python
# tests/test_api/test_templates.py
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_create_template(test_template):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/templates/", json=test_template)
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == test_template["title"]
        assert "id" in data

@pytest.mark.asyncio
async def test_create_template_invalid_data():
    async with AsyncClient(app=app, base_url="http://test") as