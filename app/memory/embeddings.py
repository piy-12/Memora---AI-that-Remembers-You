from langchain_huggingface import HuggingFaceEmbeddings


embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True}
)


STORE_INDEX = {
    "embed": embeddings,
    "dims": 384,
    "fields": ["content"]
}