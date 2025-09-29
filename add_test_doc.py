#!/usr/bin/env python3
"""Script to add test document to the vector store."""

import os
import sys

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.rag import document_manager

def add_test_document():
    """Add a test document to the vector store."""
    try:
        document_path = "test_document.txt"
        
        # Add the document
        doc_ids = document_manager.add_official_document(
            file_path=document_path,
            department="HR",
            document_type="Employee Handbook",
            additional_metadata={
                "title": "ORIN Employee Handbook - Chapter 3: Leave Policies",
                "author": "HR Department",
                "version": "1.0"
            }
        )
        
        print(f"Successfully added document with IDs: {doc_ids}")
        print("Test document has been indexed in the vector store.")
        
    except Exception as e:
        print(f"Error adding document: {e}")

if __name__ == "__main__":
    add_test_document()