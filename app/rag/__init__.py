from .vectorstore import get_vector_store
from .retriever import ORINRetriever, document_manager

# Lazy loading for vector_store
def __getattr__(name):
    if name == "vector_store":
        return get_vector_store()
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

__all__ = ["vector_store", "ORINRetriever", "document_manager", "get_vector_store"]