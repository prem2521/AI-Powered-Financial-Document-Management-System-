from app.rag.reranker import rerank_results

def test():
    query = "What is the capital of France?"
    results = [
        {"content": "Paris is the capital of France.", "metadata": {"id": 1}, "distance": 0.5},
        {"content": "London is the capital of the United Kingdom.", "metadata": {"id": 2}, "distance": 0.6},
        {"content": "France is a country in Europe.", "metadata": {"id": 3}, "distance": 0.7}
    ]
    
    reranked = rerank_results(query, results, top_k=2)
    assert len(reranked) == 2, "Should return exactly top_k results"
    assert reranked[0]["metadata"]["id"] == 1, "The most relevant document should be ranked first"
    assert "score" in reranked[0], "Reranked results should contain scores"
    
    print("Cross-encoder reranking tests passed.")

if __name__ == "__main__":
    test()
