from uuid import uuid4


def save_memory(store, user_id, category, content):

    namespace = ("users", user_id, "memories")

    memory_id = str(uuid4())

    memory = {
        "category": category,
        "content": content
    }

    store.put(
        namespace,
        memory_id,
        memory
    )

    return memory_id


def retrieve_memories(store, user_id):

    namespace = ("users", user_id, "memories")

    memories = store.search(
        namespace,
        limit=100
    )

    return [
        memory.value
        for memory in memories
    ]


def delete_memory(store, user_id, memory_id):

    namespace = ("users", user_id, "memories")

    store.delete(
        namespace,
        memory_id
    )