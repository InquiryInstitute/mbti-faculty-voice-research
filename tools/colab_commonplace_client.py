#!/usr/bin/env python3
"""
Colab Commonplace Client
Helper functions for interacting with Commonplace from Google Colab notebooks.
"""

import os
import requests
from typing import Optional, Dict, Any, List

class ColabCommonplaceClient:
    """Client for interacting with Commonplace via Supabase Edge Function."""
    
    def __init__(
        self,
        supabase_url: str,
        supabase_anon_key: str,
        jwt_token: Optional[str] = None,
        api_key: Optional[str] = None
    ):
        """
        Initialize client.
        
        Args:
            supabase_url: Supabase project URL
            supabase_anon_key: Supabase anonymous key
            jwt_token: Optional JWT token for authentication
            api_key: Optional API key for authentication (alternative to JWT)
        """
        self.supabase_url = supabase_url.rstrip('/')
        self.supabase_anon_key = supabase_anon_key
        self.jwt_token = jwt_token
        self.api_key = api_key
        self.edge_function_url = f"{self.supabase_url}/functions/v1/colab-commonplace"
        
        if not jwt_token and not api_key:
            raise ValueError("Either jwt_token or api_key must be provided")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication."""
        headers = {
            "Content-Type": "application/json",
            "apikey": self.supabase_anon_key,
        }
        
        if self.jwt_token:
            headers["Authorization"] = f"Bearer {self.jwt_token}"
        elif self.api_key:
            headers["X-Colab-API-Key"] = self.api_key
        
        return headers
    
    def create_entry(
        self,
        title: str,
        content: str,
        status: str = "draft",
        faculty_slug: Optional[str] = None,
        entry_type: Optional[str] = None,
        topics: Optional[List[str]] = None,
        college: Optional[str] = None,
        excerpt: Optional[str] = None,
        visibility: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new Commonplace entry.
        
        Args:
            title: Entry title (required)
            content: Entry content HTML (required)
            status: Entry status (draft, publish, private, pending)
            faculty_slug: Faculty slug (auto-detected from JWT if not provided)
            entry_type: Entry type slug
            topics: List of topic slugs
            college: College slug
            excerpt: Entry excerpt
            visibility: Entry visibility (public, faculty_only, private)
            metadata: Additional metadata dict
        
        Returns:
            Response dict with entry data
        """
        payload = {
            "action": "create",
            "entry": {
                "title": title,
                "content": content,
                "status": status,
            }
        }
        
        if faculty_slug:
            payload["entry"]["faculty_slug"] = faculty_slug
        if entry_type:
            payload["entry"]["entry_type"] = entry_type
        if topics:
            payload["entry"]["topics"] = topics
        if college:
            payload["entry"]["college"] = college
        if excerpt:
            payload["entry"]["excerpt"] = excerpt
        if visibility:
            payload["entry"]["visibility"] = visibility
        if metadata:
            payload["entry"]["metadata"] = metadata
        
        response = requests.post(
            self.edge_function_url,
            headers=self._get_headers(),
            json=payload,
            timeout=30
        )
        
        response.raise_for_status()
        return response.json()
    
    def update_entry(
        self,
        entry_id: int,
        title: Optional[str] = None,
        content: Optional[str] = None,
        status: Optional[str] = None,
        excerpt: Optional[str] = None,
        entry_type: Optional[str] = None,
        topics: Optional[List[str]] = None,
        college: Optional[str] = None,
        visibility: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Update an existing Commonplace entry.
        
        Args:
            entry_id: Entry ID to update
            title: New title (optional)
            content: New content (optional)
            status: New status (optional)
            excerpt: New excerpt (optional)
            entry_type: New entry type (optional)
            topics: New topics list (optional)
            college: New college (optional)
            visibility: New visibility (optional)
            metadata: New metadata (optional)
        
        Returns:
            Response dict with updated entry data
        """
        entry_updates = {}
        if title is not None:
            entry_updates["title"] = title
        if content is not None:
            entry_updates["content"] = content
        if status is not None:
            entry_updates["status"] = status
        if excerpt is not None:
            entry_updates["excerpt"] = excerpt
        if entry_type is not None:
            entry_updates["entry_type"] = entry_type
        if topics is not None:
            entry_updates["topics"] = topics
        if college is not None:
            entry_updates["college"] = college
        if visibility is not None:
            entry_updates["visibility"] = visibility
        if metadata is not None:
            entry_updates["metadata"] = metadata
        
        payload = {
            "action": "update",
            "entry_id": entry_id,
            "entry": entry_updates
        }
        
        response = requests.put(
            self.edge_function_url,
            headers=self._get_headers(),
            json=payload,
            timeout=30
        )
        
        response.raise_for_status()
        return response.json()
    
    def get_entry(self, entry_id: int) -> Dict[str, Any]:
        """
        Get a Commonplace entry by ID.
        
        Args:
            entry_id: Entry ID
        
        Returns:
            Response dict with entry data
        """
        response = requests.get(
            f"{self.edge_function_url}?entry_id={entry_id}",
            headers=self._get_headers(),
            timeout=30
        )
        
        response.raise_for_status()
        return response.json()


# Convenience function for Colab notebooks
def create_commonplace_entry(
    title: str,
    content: str,
    jwt_token: Optional[str] = None,
    api_key: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Quick function to create a Commonplace entry from Colab.
    
    Usage:
        from colab_commonplace_client import create_commonplace_entry
        
        result = create_commonplace_entry(
            title="My Essay",
            content="<p>Content...</p>",
            jwt_token="your-token",
            faculty_slug="a-lovelace",
            status="draft"
        )
    """
    supabase_url = os.getenv("NEXT_PUBLIC_SUPABASE_URL", "https://xougqdomkoisrxdnagcj.supabase.co")
    supabase_anon_key = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")
    
    if not supabase_anon_key:
        raise ValueError("NEXT_PUBLIC_SUPABASE_ANON_KEY not set")
    
    client = ColabCommonplaceClient(
        supabase_url=supabase_url,
        supabase_anon_key=supabase_anon_key,
        jwt_token=jwt_token,
        api_key=api_key
    )
    
    return client.create_entry(title=title, content=content, **kwargs)
