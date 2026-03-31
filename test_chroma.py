from app.rag.vector_store import get_collection, get_chroma_client

def test():
    client = get_chroma_client()
    assert client is not None
    collection = get_collection()
    assert collection is not None
    assert collection.name == "financial_documents"
    print("ChromaDB connection and collection initialization successful.")

if __name__ == "__main__":
    test()
