# AudioMaster Project Documentation

## Project Overview

### Summary
In this project, we are creating templates that are questionnaires. The idea is to create many different templates for questionnaires, and then people will fill them out. Filling out these questionnaires is giving us the information we will need to be able to create hyper-customized self-help audio books. Currently, we have a template manager where we can create, manage, and interact with various questionnaire templates.

## Project Architecture

### Tech Stack
- **Backend**: Flask (Python)
- **Database**: SQLAlchemy with PostgreSQL
- **Authentication**: Flask-Login
- **Form Handling**: Flask-WTF
- **API Integration**: OpenAI API

### Project Structure
```
AudioMaster/
│
├── routes/                 # Flask route handlers
│   ├── questionnaires.py   # Handles questionnaire-related routes
│   ├── templates.py        # Manages template CRUD operations
│   ├── prompts.py          # Manages prompt generation
│   └── ...
│
├── models.py               # Database models
├── app.py                  # Flask application factory
├── db_setup.py             # Database initialization
│
├── templates/              # HTML templates
│   ├── base.html           # Base template
│   ├── questionnaire_list.html
│   └── ...
│
└── services/               # Business logic and external service integrations
    └── openai_service.py   # OpenAI API interactions
```

## Key Components

### 1. Questionnaire Management
- **Purpose**: Create, store, and manage questionnaire templates
- **Key Files**: 
  - `routes/questionnaires.py`
  - `routes/templates.py`
- **Functionality**:
  - Create new questionnaire templates
  - List existing templates
  - Edit and delete templates
  - Generate prompts based on templates

### 2. Database Models
- **Key Models**:
  - `Template`: Stores questionnaire template information
  - `Questionnaire`: Stores individual questionnaire responses
  - `Prompt`: Stores generated prompts
  - `User`: User management and authentication

### 3. OpenAI Integration
- **Purpose**: Generate customized content based on questionnaire responses
- **Key Components**:
  - Prompt generation
  - Content creation for self-help audiobooks
  - Leveraging OpenAI's GPT models for intelligent content generation

## Current Achievements

### Implemented Features
1. Questionnaire Template Management
   - Create new templates
   - List and view existing templates
   - Basic CRUD operations for templates

2. OpenAI API Integration
   - Prompt generation
   - Content creation mechanisms

3. Database Management
   - SQLAlchemy ORM setup
   - Database migrations
   - User and template tracking

### Ongoing Development
- Refining questionnaire template system
- Improving OpenAI content generation
- Enhancing user experience
- Developing audiobook generation pipeline

## Technical Challenges and Solutions

### 1. Dynamic Questionnaire Generation
- **Challenge**: Creating flexible questionnaire templates
- **Solution**: Implement a dynamic template system that can adapt to different types of questionnaires

### 2. OpenAI API Interaction
- **Challenge**: Generating coherent and personalized content
- **Solution**: Develop a robust prompt engineering strategy

### 3. Data Persistence
- **Challenge**: Storing and retrieving complex questionnaire data
- **Solution**: Use SQLAlchemy's advanced ORM features and relationship mapping

## Future Roadmap
1. Enhanced Template Creation Tools
2. More Sophisticated OpenAI Prompt Engineering
3. Audiobook Generation Pipeline
4. User Personalization Features
5. Advanced Analytics and Insights

## Development Environment
- **Language**: Python 3.11
- **Framework**: Flask
- **Database**: PostgreSQL
- **Development Mode**: Continuous Integration

## Getting Started
1. Clone the repository
2. Set up virtual environment
3. Install dependencies
4. Configure `.env` file
5. Run database migrations
6. Start the Flask development server

## Contribution Guidelines
- Follow PEP 8 style guidelines
- Write comprehensive tests
- Document new features
- Maintain clean, modular code

## Notes for Developers
- Always use environment variables for sensitive information
- Regularly update dependencies
- Maintain comprehensive logging
- Focus on user experience and personalization

---

*Last Updated*: [Current Date]
*Project Status*: Active Development
