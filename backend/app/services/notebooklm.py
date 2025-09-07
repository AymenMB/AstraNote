"""
NotebookLM service for integrating with Google's NotebookLM API.
"""
import httpx
import asyncio
from typing import List, Dict, Any, Optional, BinaryIO
import structlog
from google.auth.transport.requests import Request
from google.oauth2 import service_account
import json
import time

from app.core.config import settings
from app.core.exceptions import NotebookLMException

logger = structlog.get_logger()


class NotebookLMService:
    """Service for interacting with Google's NotebookLM API."""
    
    def __init__(self):
        self.base_url = settings.NOTEBOOKLM_API_BASE_URL
        self.timeout = settings.NOTEBOOKLM_TIMEOUT
        self._credentials = None
        self._client = None
    
    async def _get_credentials(self):
        """Get authenticated credentials for Google Cloud."""
        if self._credentials is None:
            try:
                # Load service account credentials
                self._credentials = service_account.Credentials.from_service_account_file(
                    settings.GOOGLE_APPLICATION_CREDENTIALS,
                    scopes=['https://www.googleapis.com/auth/cloud-platform']
                )
                logger.info("Google Cloud credentials loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load Google Cloud credentials: {e}")
                raise NotebookLMException(f"Authentication failed: {e}")
        
        # Refresh credentials if needed
        if not self._credentials.valid:
            self._credentials.refresh(Request())
        
        return self._credentials
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get authenticated HTTP client."""
        if self._client is None:
            credentials = await self._get_credentials()
            headers = {
                "Authorization": f"Bearer {credentials.token}",
                "Content-Type": "application/json",
                "User-Agent": f"NotebookLM-RAG-System/{settings.VERSION}",
            }
            
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers=headers,
                timeout=self.timeout,
            )
        
        return self._client
    
    async def create_notebook(self, display_name: str, description: str = None) -> Dict[str, Any]:
        """
        Create a new notebook in NotebookLM.
        
        Args:
            display_name: Display name for the notebook
            description: Optional description
            
        Returns:
            Dict containing notebook information
        """
        try:
            client = await self._get_client()
            
            data = {
                "displayName": display_name,
            }
            
            if description:
                data["description"] = description
            
            response = await client.post("/notebooks", json=data)
            response.raise_for_status()
            
            notebook_data = response.json()
            logger.info(f"Created notebook: {notebook_data.get('name')}")
            
            return notebook_data
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error creating notebook: {e.response.status_code} - {e.response.text}")
            raise NotebookLMException(f"Failed to create notebook: {e.response.text}", e.response.status_code)
        except Exception as e:
            logger.error(f"Error creating notebook: {e}")
            raise NotebookLMException(f"Failed to create notebook: {e}")
    
    async def get_notebook(self, notebook_id: str) -> Dict[str, Any]:
        """
        Get notebook information.
        
        Args:
            notebook_id: ID of the notebook
            
        Returns:
            Dict containing notebook information
        """
        try:
            client = await self._get_client()
            
            response = await client.get(f"/notebooks/{notebook_id}")
            response.raise_for_status()
            
            return response.json()
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error getting notebook: {e.response.status_code} - {e.response.text}")
            raise NotebookLMException(f"Failed to get notebook: {e.response.text}", e.response.status_code)
        except Exception as e:
            logger.error(f"Error getting notebook: {e}")
            raise NotebookLMException(f"Failed to get notebook: {e}")
    
    async def upload_document(
        self, 
        notebook_id: str, 
        file_content: bytes, 
        filename: str, 
        mime_type: str
    ) -> Dict[str, Any]:
        """
        Upload a document to a notebook.
        
        Args:
            notebook_id: ID of the notebook
            file_content: Binary content of the file
            filename: Name of the file
            mime_type: MIME type of the file
            
        Returns:
            Dict containing document information
        """
        try:
            client = await self._get_client()
            
            # Prepare multipart form data
            files = {
                "file": (filename, file_content, mime_type)
            }
            
            data = {
                "displayName": filename,
            }
            
            # Update headers for multipart upload
            client.headers.update({"Content-Type": "multipart/form-data"})
            
            response = await client.post(
                f"/notebooks/{notebook_id}/documents",
                files=files,
                data=data
            )
            response.raise_for_status()
            
            document_data = response.json()
            logger.info(f"Uploaded document: {document_data.get('name')}")
            
            return document_data
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error uploading document: {e.response.status_code} - {e.response.text}")
            raise NotebookLMException(f"Failed to upload document: {e.response.text}", e.response.status_code)
        except Exception as e:
            logger.error(f"Error uploading document: {e}")
            raise NotebookLMException(f"Failed to upload document: {e}")
        finally:
            # Reset headers
            if self._client:
                self._client.headers["Content-Type"] = "application/json"
    
    async def get_document(self, notebook_id: str, document_id: str) -> Dict[str, Any]:
        """
        Get document information.
        
        Args:
            notebook_id: ID of the notebook
            document_id: ID of the document
            
        Returns:
            Dict containing document information
        """
        try:
            client = await self._get_client()
            
            response = await client.get(f"/notebooks/{notebook_id}/documents/{document_id}")
            response.raise_for_status()
            
            return response.json()
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error getting document: {e.response.status_code} - {e.response.text}")
            raise NotebookLMException(f"Failed to get document: {e.response.text}", e.response.status_code)
        except Exception as e:
            logger.error(f"Error getting document: {e}")
            raise NotebookLMException(f"Failed to get document: {e}")
    
    async def delete_document(self, notebook_id: str, document_id: str) -> bool:
        """
        Delete a document from a notebook.
        
        Args:
            notebook_id: ID of the notebook
            document_id: ID of the document
            
        Returns:
            True if successful
        """
        try:
            client = await self._get_client()
            
            response = await client.delete(f"/notebooks/{notebook_id}/documents/{document_id}")
            response.raise_for_status()
            
            logger.info(f"Deleted document: {document_id}")
            return True
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error deleting document: {e.response.status_code} - {e.response.text}")
            raise NotebookLMException(f"Failed to delete document: {e.response.text}", e.response.status_code)
        except Exception as e:
            logger.error(f"Error deleting document: {e}")
            raise NotebookLMException(f"Failed to delete document: {e}")
    
    async def query_notebook(
        self, 
        notebook_id: str, 
        query: str, 
        max_results: int = 10,
        include_sources: bool = True,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Query a notebook for information.
        
        Args:
            notebook_id: ID of the notebook
            query: Query text
            max_results: Maximum number of results
            include_sources: Whether to include source attribution
            context: Optional context for conversation
            
        Returns:
            Dict containing query results
        """
        try:
            client = await self._get_client()
            
            data = {
                "query": query,
                "maxResults": max_results,
                "includeSources": include_sources,
            }
            
            if context:
                data["context"] = context
            
            start_time = time.time()
            
            response = await client.post(f"/notebooks/{notebook_id}/query", json=data)
            response.raise_for_status()
            
            execution_time = time.time() - start_time
            
            result = response.json()
            result["executionTime"] = execution_time
            
            logger.info(f"Query executed in {execution_time:.2f}s")
            
            return result
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error querying notebook: {e.response.status_code} - {e.response.text}")
            raise NotebookLMException(f"Failed to query notebook: {e.response.text}", e.response.status_code)
        except Exception as e:
            logger.error(f"Error querying notebook: {e}")
            raise NotebookLMException(f"Failed to query notebook: {e}")
    
    async def list_documents(self, notebook_id: str) -> List[Dict[str, Any]]:
        """
        List all documents in a notebook.
        
        Args:
            notebook_id: ID of the notebook
            
        Returns:
            List of document information
        """
        try:
            client = await self._get_client()
            
            response = await client.get(f"/notebooks/{notebook_id}/documents")
            response.raise_for_status()
            
            data = response.json()
            return data.get("documents", [])
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error listing documents: {e.response.status_code} - {e.response.text}")
            raise NotebookLMException(f"Failed to list documents: {e.response.text}", e.response.status_code)
        except Exception as e:
            logger.error(f"Error listing documents: {e}")
            raise NotebookLMException(f"Failed to list documents: {e}")
    
    async def close(self):
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None


# Global service instance
notebook_service = NotebookLMService()
