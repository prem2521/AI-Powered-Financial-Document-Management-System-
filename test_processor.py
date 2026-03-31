from app.rag.document_processor import process_document

def test():
    # Test txt file processing
    with open("sample.txt", "w") as f:
        f.write("This is a sample document. It has enough content to be at least processed. " * 50)
    
    chunks = process_document("sample.txt")
    assert len(chunks) > 0, "No chunks generated from sample.txt"
    print(f"Generated {len(chunks)} chunks from text.")

    print("Document processor tests passed.")

if __name__ == "__main__":
    test()
