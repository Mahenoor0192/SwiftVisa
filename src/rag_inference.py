# src/rag_inference.py
import json
import sys
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

VECTOR_DIR = "vector_store"  # relative to repo root
EMB_MODEL = "all-MiniLM-L6-v2"
TOP_K = 5


def load_vectorstore():
    emb = HuggingFaceEmbeddings(model_name=EMB_MODEL)
    try:
        vs = FAISS.load_local(VECTOR_DIR, emb, allow_dangerous_deserialization=True)
    except Exception as e:
        print("Error loading FAISS vector store:", e, file=sys.stderr)
        raise
    return vs


def retrieve(query, k=TOP_K):
    """
    Returns a list of Document objects for the given query.
    Uses similarity_search on the FAISS vectorstore for compatibility.
    """
    vs = load_vectorstore()
    # Direct similarity search (works across LangChain versions)
    docs = vs.similarity_search(query, k=k)
    return docs


if __name__ == "__main__":
    q = "student visa eligibility for Canadian nationals"
    print("Running retrieval for query:", q)
    hits = retrieve(q, k=3)
    print(f"Returned {len(hits)} hits\n")
    for i, d in enumerate(hits, 1):
        meta = d.metadata if hasattr(d, "metadata") else {}
        text_preview = (
            d.page_content[:400] if hasattr(d, "page_content") else str(d)[:400]
        )
        print(f"--- Hit {i} ---")
        print("metadata:", meta)
        print("text preview:", text_preview.replace("\n", " "))
        print()
