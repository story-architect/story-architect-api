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
