import os

from dotenv import load_dotenv
from datetime import datetime, timezone

from langchain_core.messages import HumanMessage

from app.memory.embeddings import STORE_INDEX

from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.store.postgres import PostgresStore

from app.agent.graph import create_graph
from app.agent.context import Context


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found in environment variables.")




def main():

    user_id = "user_123"

    # One continuous thread per user
    thread_id = user_id

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    # Initialize Checkpointer and Store
    with (
        PostgresSaver.from_conn_string(DATABASE_URL) as checkpointer,
        PostgresStore.from_conn_string(
            DATABASE_URL,
            index=STORE_INDEX
        ) as store
    ):

        checkpointer.setup()
        store.setup()

        # Compile Graph
        graph = create_graph(
            checkpointer,
            store
        )

        print("\n========== MEMORA ==========")
        print("Your Personal AI Companion")
        print("Type 'exit' to quit.")
        print("============================")

        while True:

            user_input = input("\nYou: ").strip()

            if user_input.lower() in ["exit", "quit"]:
                print("\nGoodbye!")
                break

            if not user_input:
                continue

            # Attach timestamp to user message
            user_message = HumanMessage(
                content=user_input,
                additional_kwargs={
                    "created_at": datetime.now(
                        timezone.utc
                    ).isoformat()
                }
            )

            # Invoke Graph
            response = graph.invoke(
                {"messages": [user_message]},
                config=config,
                context=Context(user_id=user_id)
            )

            print(
                "\nMemora:",
                response["messages"][-1].content
            )


if __name__ == "__main__":
    main()