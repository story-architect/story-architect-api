# Story Architect Backend

This is the backend for the Story Architect MVP, built with FastAPI, PostgreSQL, SQLAlchemy, and Alembic.

## Requirements
- Python 3.10+
- PostgreSQL

## Quick Start with Docker

The easiest way to run the application is using Docker and Docker Compose.

1. **Start the services**
   ```bash
   docker compose up --build
   ```
   This will automatically:
   - Start a PostgreSQL database instance
   - Build and start the FastAPI backend
   - Run the Alembic database migrations
   - Seed the initial discovery questions into the database

2. **Access the API**
   The API documentation will be available at [http://localhost:8000/docs](http://localhost:8000/docs).

---

## Manual Setup Instructions

1. **Clone the repository and set up a virtual environment**
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Database Setup**
   Ensure you have a PostgreSQL database running locally.
   Create a database named `story_architect` (or match the name in your `.env` file).
   
   Create a `.env` file in the root directory and add your connection string:
   ```env
   DATABASE_URL=postgresql://postgres:postgres@localhost:5432/story_architect
   ```

4. **Run Migrations**
   Initialize the database schema:
   ```bash
   alembic upgrade head
   ```

5. **Seed the Database**
   Seed the initial discovery questions:
   ```bash
   python -m app.db.seed
   ```

6. **Start the Server**
   Start the FastAPI development server:
   ```bash
   uvicorn app.main:app --reload
   ```

The API documentation will be available at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

## Running Tests

We use `pytest` for testing. The tests are configured to use an in-memory SQLite database for speed and isolation.

To run the tests:
```bash
# Make sure your virtual environment is activated
pytest
```

## Linting and Formatting

We use `ruff` for linting and `black` for code formatting.

To check formatting and linting:
```bash
ruff check .
black --check .
```

To auto-format the code:
```bash
black .
ruff check . --fix
```

## Type Checking

We use `mypy` for static type checking.

To run the type checker:
```bash
mypy .
```

## SonarQube Cloud

This project is configured for static code analysis using SonarQube Cloud.
To use it in your own GitHub repository:
1. Create a project in SonarQube Cloud.
2. Update the `sonar.organization` and `sonar.projectKey` inside `sonar-project.properties`.
3. Add a secret named `SONAR_TOKEN` to your GitHub repository secrets.
The GitHub Actions workflow will automatically run the scan on pushes and pull requests.

---

## Example API Calls

**Create a Story:**
```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/api/v1/stories' \
  -H 'Content-Type: application/json' \
  -d '{
  "title": "The Last Kingdom",
  "genre": "Fantasy",
  "one_sentence_premise": "A warrior seeks to reclaim his birthright."
}'
```

**Get Discovery Questions:**
```bash
curl -X 'GET' \
  'http://127.0.0.1:8000/api/v1/discovery/questions?flow_type=CHARACTER_DISCOVERY' \
  -H 'accept: application/json'
```

---

## Product North Star & Feature Governance

This document defines the identity of Story Architect.

Its purpose is to protect the product from feature creep and ensure all future development strengthens the core vision.

### Product North Star

Story Architect helps writers discover:

* Emotional Architecture
* Dramatic Architecture
* Relationship Architecture

The product becomes valuable when it helps writers understand their stories.
The product does NOT become valuable by helping writers store more information.

Story Architect is a discovery platform.
Not a storage platform.

### Core Product Question

Before implementing any new feature ask:
"Does this help the writer discover emotional or dramatic architecture?"

If YES: The feature may belong in Story Architect.
If NO: The feature likely belongs to a different product category.

### What Makes Story Architect Different

Many writing tools help writers organize information. (e.g. Notes, Chapters, Timelines, Worldbuilding, Drafts)

Story Architect is different. Its purpose is helping writers answer questions such as:
- Who is this character?
- Why do they behave this way?
- What emotional wound drives them?
- What dramatic consequences emerge?
- What conflict naturally appears?
- What transformation is required?
- What happens when two people collide emotionally?

This is the core identity of the product.

### Product-Specific Concepts

The following concepts are part of Story Architect's unique language. These concepts should continue evolving.

Character Architecture Report, Relationship Architecture Report, Discovery Event, Discovery Journal, Pattern Emerging, Insight Unlocked, Narrative Consequence, Conflict Created, Pressure Point, Transformation Path, Relationship Risk, Relationship Cost, Relationship Turning Point, Story Engine.

These concepts are more important than generic writing features.

### Current Focus

Priority Areas:
* Emotional Architecture
* Character Discovery
* Relationship Discovery
* Discovery Events
* Discovery Journal
* Revision Support
* Refresh Architecture
* Character-Driven Dramatic Architecture
* Relationship-Driven Dramatic Architecture

The goal is depth. Not breadth.

### Features Explicitly Out Of Scope

Do NOT implement the following:
Worldbuilding, Timeline Management, Scene Planning, Chapter Planning, Draft Editor, Character Chat, Maps, Magic Systems, Lore Encyclopedias, AI Writing Assistant, Interactive Storyboards, Novel Writing Workspace, Publishing Tools.

These belong to different product categories. Adding them risks diluting Story Architect's identity.

### Product Evolution Roadmap

**Layer 1: Emotional Architecture**
Questions: What hurt this character? What do they fear? What lie protects them? What behavior emerges?
Outputs: Character Architecture, Relationship Architecture

**Layer 2: Character-Driven Dramatic Architecture**
Questions: What behavior protects the character? What consequence does it create? What conflict emerges? What pressure threatens the lie? What transformation is required?
Outputs: Narrative Consequence, Conflict Created, Pressure Point, Transformation Path, Story Engine

**Layer 3: Relationship-Driven Dramatic Architecture**
Questions: How do two character patterns interact? What relationship risk emerges? What cost exists? What turning point is required?
Outputs: Relationship Pattern, Relationship Risk, Relationship Cost, Relationship Turning Point, Relationship Engine

**Layer 4: Event-Driven Dramatic Architecture**
Questions: What event threatens the lie? What event escalates the conflict? What event breaks the pattern? What event forces transformation?
Important: Events are consequences. Events are not the starting point.
Outputs: Threatening Event, Escalation Event, Breaking Point Event, Transformation Event

### Decision Rule

When considering a new feature:

**Step 1:** Ask: "Does this deepen discovery?" If no: Reject or defer.
**Step 2:** Ask: "Does this strengthen emotional architecture?" If no: Reject or defer.
**Step 3:** Ask: "Does this strengthen dramatic architecture?" If no: Reject or defer.

### Final Principle

Story Architect should become deeper. Not broader.
The goal is not to become another writing application.
The goal is to become the best platform for discovering why stories work.
