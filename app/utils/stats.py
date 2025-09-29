"""Document statistics tracking for admin dashboard."""

import json
import os
from datetime import datetime
from typing import Dict, List, Any
from dataclasses import dataclass, asdict
from pathlib import Path

@dataclass
class DocumentStats:
    """Document statistics data class."""
    total_documents: int = 0
    documents_by_department: Dict[str, int] = None
    documents_by_type: Dict[str, int] = None
    recent_uploads: List[Dict[str, Any]] = None
    last_updated: str = None
    
    def __post_init__(self):
        if self.documents_by_department is None:
            self.documents_by_department = {}
        if self.documents_by_type is None:
            self.documents_by_type = {}
        if self.recent_uploads is None:
            self.recent_uploads = []
        if self.last_updated is None:
            self.last_updated = datetime.utcnow().isoformat()


class DocumentStatsManager:
    """Manages document statistics storage and retrieval."""
    
    def __init__(self, stats_file: str = "document_stats.json"):
        """Initialize the stats manager."""
        self.stats_file = Path(stats_file)
        self.stats = self._load_stats()
    
    def _load_stats(self) -> DocumentStats:
        """Load statistics from file."""
        if self.stats_file.exists():
            try:
                with open(self.stats_file, 'r') as f:
                    data = json.load(f)
                    return DocumentStats(**data)
            except Exception as e:
                print(f"Error loading stats: {e}")
        return DocumentStats()
    
    def _save_stats(self):
        """Save statistics to file."""
        try:
            with open(self.stats_file, 'w') as f:
                json.dump(asdict(self.stats), f, indent=2)
        except Exception as e:
            print(f"Error saving stats: {e}")
    
    def add_document(self, metadata: Dict[str, Any]):
        """Add a document to the statistics."""
        # Update total count
        self.stats.total_documents += 1
        
        # Update department stats
        department = metadata.get('department', 'unknown')
        self.stats.documents_by_department[department] = (
            self.stats.documents_by_department.get(department, 0) + 1
        )
        
        # Update document type stats
        doc_type = metadata.get('document_type', 'unknown')
        self.stats.documents_by_type[doc_type] = (
            self.stats.documents_by_type.get(doc_type, 0) + 1
        )
        
        # Add to recent uploads (keep only last 10)
        upload_info = {
            "filename": metadata.get('filename', 'Unknown'),
            "department": department,
            "document_type": doc_type,
            "uploaded_by": metadata.get('uploaded_by', 'Unknown'),
            "uploaded_at": metadata.get('uploaded_at', datetime.utcnow().isoformat()),
            "size": metadata.get('size', 0)
        }
        
        self.stats.recent_uploads.insert(0, upload_info)
        self.stats.recent_uploads = self.stats.recent_uploads[:10]  # Keep only last 10
        
        # Update timestamp
        self.stats.last_updated = datetime.utcnow().isoformat()
        
        # Save to file
        self._save_stats()
    
    def get_stats(self) -> DocumentStats:
        """Get current statistics."""
        return self.stats
    
    def reset_stats(self):
        """Reset all statistics."""
        self.stats = DocumentStats()
        self._save_stats()


# Global stats manager instance
stats_manager = DocumentStatsManager()