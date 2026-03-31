"""
API Client - Manages requests session and configuration for API automation.
"""

from typing import Optional, Dict, Any

import requests
from requests import Session

from src.core.base_client import BaseClient
from src.core.exceptions import APIConnectionError


class APIClient(BaseClient):
    """
    API Client for managing HTTP requests.
    
    Handles:
    - Session management
    - Base URL management
    - Default headers and authentication
    - Connection pooling
    
    Usage:
        client = APIClient(base_url="https://api.example.com")
        client.set_auth_token("my_token")
        endpoint = UserEndpoint(client.session, client.base_url)
        user = endpoint.get_user(1)
    """

    def __init__(self, base_url: Optional[str] = None):
        """
        Initialize API Client.
        
        Args:
            base_url: Base URL for API (from config if not provided)
        """
        super().__init__(client_name="APIClient")

        if base_url is None:
            base_url = self.config.get("api_base_url", "")

        self.base_url = base_url
        self.session = requests.Session()
        self.default_headers: Dict[str, str] = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        self._logger.debug(f"APIClient initialized with base_url: {base_url}")
        self._is_initialized = True

    def set_default_headers(self, headers: Dict[str, str]) -> None:
        """
        Set default headers for all requests.
        
        Args:
            headers: Headers dictionary
        """
        self.default_headers.update(headers)
        self.session.headers.update(headers)
        self._logger.debug(f"Set default headers: {list(headers.keys())}")

    def set_auth_token(self, token: str, auth_type: str = "Bearer") -> None:
        """
        Set authentication token.
        
        Args:
            token: Authentication token
            auth_type: Authentication type (Bearer, Basic, etc.)
        """
        auth_header = {
            "Authorization": f"{auth_type} {token}"
        }
        self.set_default_headers(auth_header)
        self._logger.debug(f"Set {auth_type} authentication")

    def set_timeout(self, timeout: int) -> None:
        """
        Set default timeout for requests.
        
        Args:
            timeout: Timeout in seconds
        """
        self.session.timeout = timeout
        self._logger.debug(f"Set request timeout: {timeout}s")

    def close(self) -> None:
        """Close API session."""
        if self.session:
            self.session.close()
            self._logger.debug("Closed API session")
        super().close()

    def __repr__(self) -> str:
        """String representation."""
        return f"APIClient(base_url={self.base_url}, initialized={self._is_initialized})"
