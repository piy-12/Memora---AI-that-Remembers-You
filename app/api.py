import os

from contextlib import asynccontextmanager, ExitStack
from datetime import datetime, timezone

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from langchain_core.messages import HumanMessage

from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.store.postgres import PostgresStore

from app.agent.graph import create_graph
from app.agent.context import Context
from app.memory.embeddings import STORE_INDEX


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


# ------------------------------------------------
# APPLICATION LIFESPAN
# ------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):

    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL not configured")

    with ExitStack() as stack:

        # Initialize PostgreSQL Checkpointer
        checkpointer = stack.enter_context(
            PostgresSaver.from_conn_string(DATABASE_URL)
        )

        # Initialize PostgreSQL Store
        store = stack.enter_context(
            PostgresStore.from_conn_string(
                DATABASE_URL,
                index=STORE_INDEX
            )
        )

        checkpointer.setup()
        store.setup()

        # Compile LangGraph
        graph = create_graph(
            checkpointer,
            store
        )

        app.state.graph = graph

        print("Memora LangGraph initialized successfully.")

        yield

    print("Memora application shutdown.")


# ------------------------------------------------
# FASTAPI APPLICATION
# ------------------------------------------------

app = FastAPI(
    title="Memora API",
    description="Personalized AI Companion powered by LangGraph",
    version="1.0.0",
    lifespan=lifespan
)


# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# ------------------------------------------------
# REQUEST / RESPONSE MODELS
# ------------------------------------------------

class ChatRequest(BaseModel):

    user_id: str

    message: str = Field(
        min_length=1,
        max_length=10000
    )


class ChatResponse(BaseModel):

    user_id: str

    response: str


# ------------------------------------------------
# HEALTH ENDPOINT
# ------------------------------------------------

@app.get("/health")
def health():

    return {
        "status": "healthy",
        "application": "Memora"
    }


# ------------------------------------------------
# CHAT ENDPOINT
# ------------------------------------------------

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):

    try:

        graph = app.state.graph

        user_id = request.user_id

        # One continuous conversation per user
        config = {
            "configurable": {
                "thread_id": user_id
            }
        }

        # Attach timestamp to user message
        user_message = HumanMessage(
            content=request.message,
            additional_kwargs={
                "created_at": datetime.now(
                    timezone.utc
                ).isoformat()
            }
        )

        # Execute LangGraph
        result = graph.invoke(
            {
                "messages": [user_message]
            },
            config=config,
            context=Context(user_id=user_id)
        )

        assistant_message = result["messages"][-1]

        return ChatResponse(
            user_id=user_id,
            response=assistant_message.content
        )

    except Exception as e:

        print(f"Chat error: {e}")

        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your message."
        )


# ------------------------------------------------
# CONVERSATION HISTORY ENDPOINT
# ------------------------------------------------

@app.get("/history/{user_id}")
def get_history(user_id: str):

    try:

        graph = app.state.graph

        config = {
            "configurable": {
                "thread_id": user_id
            }
        }

        # Retrieve saved graph state
        snapshot = graph.get_state(config)

        messages = snapshot.values.get(
            "messages",
            []
        )

        history = []

        for message in messages:

            if message.type == "human":
                role = "user"

            elif message.type == "ai":
                role = "assistant"

            else:
                continue

            history.append({
                "role": role,
                "content": message.content,
                "created_at": message.additional_kwargs.get(
                    "created_at"
                )
            })

        return {
            "user_id": user_id,
            "messages": history
        }

    except Exception as e:

        print(f"History error: {e}")

        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve conversation history."
        )