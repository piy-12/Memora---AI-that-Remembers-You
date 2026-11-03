# Memora – Personal AI Companion

Memora is a personal AI companion designed to maintain conversations across multiple sessions. Unlike traditional chatbots that treat every interaction independently, Memora uses **LangGraph and PostgreSQL Checkpointing** to preserve conversational context and allow the AI to refer to previous discussions.

The goal is to build an AI companion that can understand conversations over time, remember relevant details, and provide more contextual responses.

## Features

* **Persistent Conversational Memory:** Maintains conversation history across multiple sessions using LangGraph Checkpointing.
* **Context-Aware Responses:** Uses previous conversation messages to generate relevant and personalized responses.
* **Continuous Conversations:** Allows users to continue conversations without manually providing previous context.
* **Conversation History:** Separate history interface to view previously stored conversations.
* **REST API:** FastAPI backend for handling chat requests and retrieving conversation history.
* **Interactive Chat Interface:** React-based frontend for interacting with the AI companion.

## Tech Stack

| Category             | Technologies                                      |
| -------------------- | ------------------------------------------------- |
| Language             | Python, JavaScript                                |
| AI Orchestration     | LangGraph, LangChain                              |
| LLM                  | Llama 3.2 3B                                      |
| LLM Runtime          | Ollama                                            |
| Backend              | FastAPI                                           |
| Database             | PostgreSQL                                        |
| Memory & Persistence | LangGraph PostgresSaver, PostgreSQL Checkpointing |
| Frontend             | React, Vite                                       |
| API Communication    | REST API                                          |

## Architecture

```text
                 USER
                   |
                   v
            React Frontend
                   |
                   v
              FastAPI
                   |
                   v
             LangGraph
                   |
                   v
             Chatbot Node
                   |
                   v
              Llama 3.2
                (Ollama)
                   |
                   v
            Response Generation
                   |
                   v
             React Frontend


       PostgreSQL Checkpointer
                   |
                   v
         Persistent Graph State
                   |
                   v
       Previous Conversation Messages
```

## How Memory Works

Memora uses LangGraph's persistence mechanism to maintain conversation state.

1. Every incoming user message is added to the graph state.
2. LangGraph retrieves the previously checkpointed state using a `thread_id`.
3. The chatbot receives the system instructions and conversation messages.
4. The LLM generates a response using the available conversational context.
5. The updated graph state is persisted in PostgreSQL through `PostgresSaver`.

Each conversation is associated with a `thread_id`, allowing the application to restore previous messages when the user returns.

**Important:** PostgreSQL Checkpointing handles persistence, while the LLM uses the restored message history as its conversational context. This implementation currently passes the complete conversation history to the LLM rather than using semantic retrieval.

## Project Structure

```text
Memora/
│
├── app/
│   ├── agent/
│   │   ├── graph.py
│   │   ├── state.py
│   │   ├── nodes.py
│   │   └── context.py
│   │
│   ├── memory/
│   │   ├── __init__.py
│   │   ├── long_term.py
│   │   └── embeddings.py
│   │
│   ├── llm/
│   │   └── model.py
│   │
│   ├── main.py
│   └── api.py
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   └── index.css
│   │
│   ├── package.json
│   └── index.html
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Installation and Setup

### Prerequisites

Make sure you have installed:

* Python 3.10+
* Node.js and npm
* PostgreSQL
* Ollama

### 1. Clone the Repository

```bash
git clone YOUR_REPOSITORY_URL
cd Memora
```

### 2. Set Up Python Environment

```bash
python -m venv venv
```

Activate the environment on Windows:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/memora
```

Replace the database credentials with your local PostgreSQL configuration.

### 4. Configure PostgreSQL

Create a database named `memora`:

```sql
CREATE DATABASE memora;
```

Enable the required PostgreSQL extension:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

The application uses PostgreSQL for persistent LangGraph state.

### 5. Set Up Ollama

Install Ollama and download the model:

```bash
ollama pull llama3.2:3b
```

Start the Ollama service:

```bash
ollama serve
```

### 6. Run the Backend

From the project root:

```bash
uvicorn app.api:app --reload
```

The FastAPI server will run at:

```text
http://127.0.0.1:8000
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

### 7. Run the Frontend

Open another terminal:

```bash
cd frontend
npm install
```

Create a `.env` file inside the frontend directory:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

Start the development server:

```bash
npm run dev
```

Open the frontend in your browser using the URL provided by Vite.

## Current Implementation

* LangGraph-based conversational workflow.
* PostgreSQL-backed graph state persistence.
* Llama 3.2 3B integration through Ollama.
* FastAPI endpoints for chat and conversation history.
* React-based chat interface.
* Separate Chat and History pages.

## Future Improvements

* Multi-user authentication using JWT.
* User-specific conversation isolation.
* Improved long-term memory and selective context retrieval.
* Better temporal understanding of user preferences, goals, and interests.
* Conversation summarization for handling longer histories.

## Learning Objectives

This project explores practical implementation of:

* Stateful AI applications using LangGraph.
* LLM integration with locally hosted models.
* Persistent conversational memory.
* PostgreSQL-backed graph checkpointing.
* REST API development using FastAPI.
* Frontend and backend integration.

---

**Memora – An AI companion that remembers your conversations.**
