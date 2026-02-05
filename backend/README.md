# AI-Powered Todo Chatbot - Backend

A natural language todo list manager powered by OpenAI's function calling and MCP (Model Context Protocol).

## Features

- **Natural Language Interface**: Create, list, complete, update, and delete tasks through conversational messages
- **AI-Powered**: Uses OpenAI's GPT models with function calling for intelligent task management
- **MCP Tools**: Implements task operations as Model Context Protocol tools
- **Conversation History**: Maintains multi-turn conversation context
- **Stateless Architecture**: All state persisted to PostgreSQL (Neon compatible)

## Prerequisites

- Python 3.11+
- PostgreSQL database (Neon recommended)
- OpenAI API key

## Setup

### 1. Clone and Navigate

```bash
cd backend
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
DATABASE_URL=postgresql+asyncpg://user:password@host:port/database
OPENAI_API_KEY=sk-your-openai-api-key
```

### 5. Run the Application

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`.

## API Endpoints

### Authentication Endpoints

All protected endpoints require a valid JWT access token in the `Authorization` header:
```
Authorization: Bearer <access_token>
```

#### Register

```
POST /api/auth/register
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response (201):**
```json
{
  "id": "uuid-here",
  "email": "user@example.com",
  "created_at": "2026-01-21T10:00:00Z"
}
```

#### Login

```
POST /api/auth/login
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 900,
  "user": {
    "id": "uuid-here",
    "email": "user@example.com"
  }
}
```

Sets `refresh_token` HTTP-only cookie (7-day expiry).

#### Refresh Token

```
POST /api/auth/refresh
```

No request body needed. Reads `refresh_token` from cookie.

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 900
}
```

#### Logout

```
POST /api/auth/logout
```

Requires `Authorization` header. Revokes refresh token and clears cookie.

**Response (200):**
```json
{
  "message": "Successfully logged out"
}
```

#### Get Current User

```
GET /api/auth/me
```

Requires `Authorization` header.

**Response (200):**
```json
{
  "id": "uuid-here",
  "email": "user@example.com",
  "created_at": "2026-01-21T10:00:00Z"
}
```

### Chat Endpoint (Protected)

```
POST /api/chat
```

Requires `Authorization` header.

**Request Body:**
```json
{
  "message": "Add a task to buy groceries",
  "conversation_id": null
}
```

**Response:**
```json
{
  "conversation_id": "uuid-here",
  "response": "I've added 'buy groceries' to your task list!",
  "tool_calls": [
    {
      "tool_name": "add_task",
      "arguments": {"title": "buy groceries"},
      "result": "Task 'buy groceries' created successfully"
    }
  ]
}
```

### Tasks Endpoint (Protected)

```
GET /api/tasks
```

Requires `Authorization` header. Returns tasks owned by the authenticated user.

**Response:**
```json
{
  "tasks": [
    {
      "id": "uuid-here",
      "title": "buy groceries",
      "is_completed": false,
      "created_at": "2026-01-21T10:00:00Z",
      "updated_at": "2026-01-21T10:00:00Z"
    }
  ],
  "total": 1,
  "completed": 0,
  "pending": 1
}
```

### Health Check

```
GET /health
```

## Example Conversations

### Create a Task
```
User: Add a task to buy groceries
Bot: I've added 'buy groceries' to your task list!
```

### List Tasks
```
User: Show my tasks
Bot: Here are your tasks (0 completed, 1 pending):
[ ] buy groceries
```

### Complete a Task
```
User: I finished buying groceries
Bot: Great job! Task 'buy groceries' has been marked as complete.
```

### Update a Task
```
User: Change "buy groceries" to "buy groceries and milk"
Bot: Done! I've updated 'buy groceries' to 'buy groceries and milk'.
```

### Delete a Task
```
User: Delete the groceries task
Bot: Done! I've removed 'buy groceries and milk' from your task list.
```

## Project Structure

```
backend/
├── src/
│   ├── agent/              # OpenAI agent configuration
│   │   ├── __init__.py     # System prompt
│   │   └── todo_agent.py   # Agent with function calling
│   ├── api/                # FastAPI endpoints
│   │   ├── __init__.py     # Request/Response models
│   │   ├── auth.py         # Authentication endpoints
│   │   ├── chat.py         # Chat endpoint (protected)
│   │   ├── deps.py         # FastAPI dependencies
│   │   └── tasks.py        # Tasks endpoint (protected)
│   ├── core/               # Core configuration
│   │   ├── config.py       # Settings using Pydantic
│   │   ├── exceptions.py   # Custom auth exceptions
│   │   └── rate_limit.py   # Rate limiting setup
│   ├── db/                 # Database configuration
│   │   ├── __init__.py     # Async engine setup
│   │   ├── init.py         # Table initialization
│   │   └── session.py      # Session factory
│   ├── mcp/                # MCP server and tools
│   │   ├── server.py       # Tool registration
│   │   └── tools/          # Individual MCP tools
│   │       ├── add_task.py
│   │       ├── list_tasks.py
│   │       ├── complete_task.py
│   │       ├── update_task.py
│   │       ├── delete_task.py
│   │       └── utils.py
│   ├── models/             # SQLModel definitions
│   │   ├── user.py         # User and RefreshToken models
│   │   ├── task.py
│   │   ├── conversation.py
│   │   └── message.py
│   ├── services/           # Business logic
│   │   └── auth.py         # Auth service (JWT, passwords)
│   └── main.py             # FastAPI application entry
├── tests/                  # Test suite
│   ├── unit/
│   └── integration/
├── .env.example
├── pyproject.toml
├── requirements.txt
└── README.md
```

## MCP Tools

| Tool | Description |
|------|-------------|
| `add_task` | Create a new task with title |
| `list_tasks` | List all tasks with completion status |
| `complete_task` | Mark a task as complete |
| `update_task` | Update a task's title |
| `delete_task` | Remove a task |

## Database Models

### User
- `id`: UUID primary key
- `email`: Unique email address
- `password_hash`: bcrypt-hashed password
- `is_active`: Account status
- `created_at`, `updated_at`: Timestamps

### RefreshToken
- `id`: UUID primary key (used as JWT `jti`)
- `user_id`: Foreign key to User
- `token_hash`: SHA-256 hash of token
- `expires_at`: Expiration timestamp
- `revoked_at`: When revoked (null if active)
- `replaced_by`: Token that replaced this one
- `created_at`: Timestamp

### Task
- `id`: UUID primary key
- `user_id`: Legacy owner identifier
- `owner_id`: Foreign key to User (nullable)
- `title`: Task description
- `is_completed`: Completion status
- `created_at`, `updated_at`: Timestamps

### Conversation
- `id`: UUID primary key
- `user_id`: Legacy owner identifier
- `owner_id`: Foreign key to User (nullable)
- `created_at`, `updated_at`: Timestamps

### Message
- `id`: UUID primary key
- `conversation_id`: Parent conversation
- `role`: user | assistant
- `content`: Message text
- `tool_calls`: JSON array of tool invocations
- `created_at`: Timestamp

## Development

### Run with Auto-Reload

```bash
uvicorn src.main:app --reload
```

### Check OpenAPI Docs

Visit `http://localhost:8000/docs` for interactive API documentation.

## License

MIT
