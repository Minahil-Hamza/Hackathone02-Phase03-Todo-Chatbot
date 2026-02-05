# AI Todo Chatbot - Frontend

A modern, responsive chat interface for the AI-powered Todo Chatbot built with Next.js 14, TypeScript, and Tailwind CSS.

## Features

- Real-time chat interface with the AI Todo Assistant
- Responsive design (mobile-first)
- Dark mode support
- Message animations and loading states
- Tool call indicators showing which MCP tools were used
- Persistent user ID across sessions
- Auto-scrolling chat history

## Prerequisites

- Node.js 18+
- Backend server running on http://localhost:8000

## Setup

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure Environment (Optional)

Create a `.env.local` file if you need to change the API URL:

```bash
cp .env.example .env.local
```

Edit `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Run Development Server

```bash
npm run dev
```

The app will be available at http://localhost:3000

## Usage

1. Make sure the backend server is running (`uvicorn src.main:app --reload` in the backend directory)
2. Open http://localhost:3000 in your browser
3. Start chatting with the AI Todo Assistant

### Example Commands

- **Create a task**: "Add a task to buy groceries"
- **List tasks**: "Show my tasks" or "What are my todos?"
- **Complete a task**: "Mark groceries as done" or "I finished buying groceries"
- **Update a task**: "Change 'buy groceries' to 'buy groceries and milk'"
- **Delete a task**: "Remove the groceries task"

## Project Structure

```
frontend/
├── src/
│   ├── app/
│   │   ├── globals.css    # Global styles and Tailwind
│   │   ├── layout.tsx     # Root layout
│   │   └── page.tsx       # Main page
│   ├── components/
│   │   ├── Chat.tsx       # Main chat container
│   │   ├── ChatInput.tsx  # Message input component
│   │   └── ChatMessage.tsx # Message bubble component
│   └── lib/
│       └── api.ts         # API client for backend
├── package.json
├── tailwind.config.ts
├── tsconfig.json
└── next.config.js
```

## Build for Production

```bash
npm run build
npm start
```

## Technologies

- **Next.js 14** - React framework with App Router
- **TypeScript** - Type safety
- **Tailwind CSS** - Utility-first styling
- **React Hooks** - State management

## License

MIT
