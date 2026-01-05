from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    Docx2txtLoader
)

def load_document(file_path):
    if file_path.endswith(".pdf"):
        return PyPDFLoader(file_path).load()
    elif file_path.endswith(".docx"):
        return Docx2txtLoader(file_path).load()
    else:
        return TextLoader(file_path).load()
    return TextLoader(file_path, encoding="utf-8", autodetect_encoding=True).load()

