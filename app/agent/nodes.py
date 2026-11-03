from datetime import datetime, timezone
from uuid import uuid4

from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
    AIMessage
)

from langgraph.runtime import Runtime

from app.llm.model import llm
from app.agent.context import Context


SYSTEM_PROMPT = """
You are Memora, a personal AI companion.

Your personality:
- Friendly, natural, intelligent and conversational.
- Speak like a human companion, not a customer support bot.
- Be concise and avoid unnecessary explanations.
- Do not repeat greetings in every response.

MEMORY GUIDELINES:
- You have access to historical information about the user.
- Use memories ONLY when they are relevant to the current conversation.
- Do not mention personal information just to demonstrate that you remember it.
- Do not repeat the user's background, goals, interests or projects unnecessarily.
- Do not summarize previous conversations unless explicitly asked.
- Do not ask the user to confirm information you already know.
- Do not repeatedly ask the same questions.
- If a memory is not relevant, completely ignore it.

CONVERSATION GUIDELINES:
- Answer the user's actual question first.
- For simple factual questions, provide direct factual answers.
- For technical questions, focus on the technical problem.
- For personal questions, use relevant historical context.
- Ask follow-up questions only when genuinely necessary.
- Never force a conversation when the user has not invited one.
- Avoid unnecessary greetings such as "Good morning" in every response.

CHRONOLOGICAL UNDERSTANDING:
- Historical messages contain timestamps.
- Use timestamps when understanding how the user's opinions, goals,
  interests and circumstances have changed.
- Distinguish between past and current situations.
- Compare historical information only when relevant or requested.

ACCURACY:
- Never invent personal information.
- Treat user statements as user-reported information.
- If you don't know something, say so.

IMPORTANT:
Your primary responsibility is to answer the user's current message.
Memory should improve your answers, not dominate them.
"""


def format_conversation_history(messages):

    history = []

    for message in messages:

        if isinstance(message, HumanMessage):
            role = "User"

        elif isinstance(message, AIMessage):
            role = "Memora"

        else:
            continue

        timestamp = message.additional_kwargs.get(
            "created_at",
            "Timestamp unavailable"
        )

        history.append(
            f"[{timestamp}] {role}: {message.content}"
        )

    return "\n".join(history)


def chatbot(state, runtime: Runtime[Context]):

    user_id = runtime.context.user_id

    namespace = ("users", user_id, "memories")

    latest_message = next(
        (
            message
            for message in reversed(state["messages"])
            if isinstance(message, HumanMessage)
        ),
        None
    )

    if latest_message is None:
        return {}

    user_message = latest_message.content

    if not isinstance(user_message, str):
        return {}

    # Retrieve relevant historical memories
    memories = runtime.store.search(
        namespace,
        query=user_message,
        limit=5
    )

    memory_context = "\n".join(
        [
            (
                f"[{memory.value.get('created_at', 'Timestamp unavailable')}] "
                f"{memory.value.get('content', '')}"
            )
            for memory in memories
        ]
    )

    # Save current user message
    created_at = latest_message.additional_kwargs.get(
        "created_at",
        datetime.now(timezone.utc).isoformat()
    )

    runtime.store.put(
        namespace,
        str(uuid4()),
        {
            "content": user_message,
            "created_at": created_at
        }
    )

    # Construct system prompt
    system_message = SystemMessage(
        content=f"""
{SYSTEM_PROMPT}

RELEVANT USER MEMORIES:
{memory_context if memory_context else "No relevant memories found."}

Use these memories only when relevant to the current message.
"""
    )

    # Generate response using only current message and relevant memories
    response = llm.invoke(
        [
            system_message,
            *state["messages"]
        ]
    )

    return {
        "messages": [response]
    }