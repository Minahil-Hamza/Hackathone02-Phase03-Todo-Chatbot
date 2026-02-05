# AI-Powered Todo Chatbot

A natural language todo list manager powered by OpenAI's function calling and MCP (Model Context Protocol). Built with FastAPI backend and Next.js frontend.

## Features

- **Natural Language Interface**: Manage tasks through conversational messages
- **AI-Powered**: Uses OpenAI GPT-4o-mini with function calling for intelligent task management
- **MCP Tools**: Task operations implemented as Model Context Protocol tools
- **Conversation History**: Maintains multi-turn conversation context
- **Modern UI**: Responsive chat interface with dark mode support
- **Stateless Architecture**: All state persisted to PostgreSQL (Neon compatible)

## Architecture

```
┌─────────────────┐     ┌──────────────────────────────────────────────────┐
│  Next.js UI     │     │              FastAPI Server                       │
│  (Frontend)     │────▶│  Chat Endpoint → OpenAI Agent → MCP Tools        │
└─────────────────┘     └──────────────────────────────────────────────────┘
                                               │
                                               ▼
                        ┌─────────────────────────────────────────────────┐
                        │              Neon PostgreSQL                     │
                        │  Tables: tasks, conversations, messages          │
                        └─────────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL database (Neon recommended)
- OpenAI API key

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your DATABASE_URL and OPENAI_API_KEY

# Run server
uvicorn src.main:app --reload
```

Backend runs at http://localhost:8000

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Frontend runs at http://localhost:3000

## Usage Examples

| Command | Action |
|---------|--------|
| "Add a task to buy groceries" | Creates a new task |
| "Show my tasks" | Lists all tasks |
| "I finished buying groceries" | Marks task as complete |
| "Change groceries to groceries and milk" | Updates task title |
| "Delete the groceries task" | Removes the task |

## API Endpoints

### Chat
```
POST /api/{user_id}/chat
```

Request:
```json
{
  "message": "Add a task to buy groceries",
  "conversation_id": null
}
```

Response:
```json
{
  "conversation_id": "uuid",
  "response": "I've added 'buy groceries' to your task list!",
  "tool_calls": [...]
}
```

### Health Check
```
GET /health
```

## MCP Tools

| Tool | Description |
|------|-------------|
| `add_task` | Create a new task |
| `list_tasks` | List all tasks with status |
| `complete_task` | Mark a task as complete |
| `update_task` | Update a task's title |
| `delete_task` | Remove a task |

## Project Structure

```
.
├── backend/           # FastAPI backend
│   ├── src/
│   │   ├── agent/     # OpenAI agent
│   │   ├── api/       # Chat endpoint
│   │   ├── db/        # Database config
│   │   ├── mcp/       # MCP server & tools
│   │   └── models/    # SQLModel entities
│   └── README.md
├── frontend/          # Next.js frontend
│   ├── src/
│   │   ├── app/       # App router pages
│   │   ├── components/# React components
│   │   └── lib/       # API client
│   └── README.md
├── specs/             # Spec-driven development artifacts
│   └── 001-mcp-todo-chatbot/
│       ├── spec.md    # Feature specification
│       ├── plan.md    # Implementation plan
│       └── tasks.md   # Task breakdown
└── README.md          # This file
```

## Deployment

Deploy the AI Todo Chatbot to production:

| Component | Platform | Guide |
|-----------|----------|-------|
| Frontend | Vercel | [Deploy to Vercel](#deploy-frontend-to-vercel) |
| Backend | Render | [Deploy to Render](#deploy-backend-to-render) |
| Database | Neon | Already configured |

### Quick Deploy

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

### Deploy Backend to Render

1. Create a new **Web Service** on [Render](https://render.com)
2. Connect your GitHub repository
3. Configure:
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables:
   - `DATABASE_URL`: Your Neon connection string
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `ENVIRONMENT`: `production`

### Deploy Frontend to Vercel

1. Import project on [Vercel](https://vercel.com)
2. Configure:
   - **Root Directory**: `frontend`
   - **Framework**: Next.js (auto-detected)
3. Add environment variable:
   - `NEXT_PUBLIC_API_URL`: Your Render backend URL

### Detailed Guide

See [DEPLOYMENT.md](./DEPLOYMENT.md) for complete deployment instructions including:
- Step-by-step setup
- Environment variables reference
- Troubleshooting guide
- Cost estimates
- Custom domain configuration

## Development

See individual README files in `backend/` and `frontend/` directories for detailed development instructions.

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 14, React 18, Tailwind CSS |
| Backend | FastAPI, Python 3.11 |
| AI | OpenAI GPT-4o-mini, Function Calling |
| Protocol | MCP (Model Context Protocol) |
| Database | Neon PostgreSQL, SQLModel |
| Hosting | Vercel (Frontend), Render (Backend) |

## License

MIT
