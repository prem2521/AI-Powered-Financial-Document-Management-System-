from app.rag.search import semantic_search
from app.rag.embeddings import get_embeddings_model
from app.rag.vector_store import get_collection

def test():
    # Insert a dummy chunk to search for
    collection = get_collection()
    embeddings_model = get_embeddings_model()
    text = "The financial risk associated with a high debt ratio is immense."
    emb = embeddings_model.embed_documents([text])
    
    collection.add(
        embeddings=emb,
        documents=[text],
        metadatas=[{"document_id": "dummy_123", "chunk_index": 0}],
        ids=["dummy_123_chunk_0"]
    )
    
    # Search
    results = semantic_search("financial risk", n_results=1)
    
    assert len(results) > 0, "No results found"
    assert "content" in results[0]
    assert "metadata" in results[0]
    assert results[0]["metadata"]["document_id"] == "dummy_123"
    
    # Clean up
    collection.delete(where={"document_id": "dummy_123"})
    print("Semantic search logic tests passed.")

if __name__ == "__main__":
    test()
