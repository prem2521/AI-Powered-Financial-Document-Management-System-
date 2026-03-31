import os
from fastapi import UploadFile
from io import BytesIO
from app.services.storage import save_upload_file, delete_file, UPLOAD_DIR

class MockUploadFile:
    def __init__(self, filename, content):
        self.filename = filename
        self.file = BytesIO(content)

def test():
    file_name = "test_doc.txt"
    mock_file = MockUploadFile(filename=file_name, content=b"Hello World")
    
    # Save file
    file_path = save_upload_file(mock_file, file_name)
    assert os.path.exists(file_path), "File was not saved"
    
    with open(file_path, "rb") as f:
        content = f.read()
        assert content == b"Hello World", "Content mismatch"

    # Delete file
    deleted = delete_file(file_path)
    assert deleted, "File should be deleted"
    assert not os.path.exists(file_path), "File should not exist"
    
    print("Storage utility tests passed.")

if __name__ == "__main__":
    test()
