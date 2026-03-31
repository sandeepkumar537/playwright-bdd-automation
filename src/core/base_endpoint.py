"""
Base endpoint class for API automation using requests library.
Provides common API request handling patterns.
"""

from typing import Any, Optional, Dict
import json

from requests import Response, Session

from src.core.base_client import BaseClient
from src.core.enums import HTTPMethod, ContentType
from src.core.exceptions import (
    APIResponseError,
    APIValidationError,
    APIConnectionError,
)


class BaseEndpoint(BaseClient):
    """
    Base class for API endpoints.
    
    Provides:
    - Request building and sending
    - Response parsing and validation
    - Status code checking
    - Header/auth handling
    - Error handling
    
    Usage:
        class UserEndpoint(BaseEndpoint):
            def __init__(self, session: Session, base_url: str):
                super().__init__(client_name="UserEndpoint")
                self.session = session
                self.base_url = base_url
                
            def get_user(self, user_id: int) -> dict:
                return self.request(
                    HTTPMethod.GET,
                    f"/users/{user_id}",
                    expected_status=200
                )
    """

    def __init__(
        self,
        session: Optional[Session] = None,
        base_url: str = "",
        endpoint_name: str = "BaseEndpoint",
    ):
        """
        Initialize endpoint.
        
        Args:
            session: Requests Session object
            base_url: Base URL for API
            endpoint_name: Name of endpoint for logging
        """
        super().__init__(client_name=endpoint_name)
        self.session = session
        self.base_url = base_url
        self.default_headers: Dict[str, str] = {}
        self._is_initialized = True

    def set_default_headers(self, headers: Dict[str, str]) -> None:
        """
        Set default headers for all requests.
        
        Args:
            headers: Headers dictionary
        """
        self.default_headers.update(headers)
        self._logger.debug(f"Set default headers: {list(headers.keys())}")

    def set_auth_header(self, token: str, auth_type: str = "Bearer") -> None:
        """
        Set authentication header.
        
        Args:
            token: Authentication token
            auth_type: Authentication type (Bearer, Basic, etc.)
        """
        self.set_default_headers({"Authorization": f"{auth_type} {token}"})
        self._logger.debug(f"Set {auth_type} authentication")

    def request(
        self,
        method: HTTPMethod,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        expected_status: int = 200,
        timeout: int = 30,
    ) -> Response:
        """
        Make API request.
        
        Args:
            method: HTTP method
            endpoint: API endpoint (path)
            data: Form data
            json_data: JSON body
            params: Query parameters
            headers: Request headers (merged with defaults)
            expected_status: Expected HTTP status code
            timeout: Request timeout (seconds)
            
        Returns:
            Response object
            
        Raises:
            APIConnectionError: If connection fails
            APIResponseError: If status code doesn't match expected
        """
        try:
            url = self._build_url(endpoint)
            request_headers = self._build_headers(headers)

            self._logger.debug(
                f"Sending {method.value} request to {url} "
                f"with headers: {list(request_headers.keys())}"
            )

            response = self.session.request(
                method=method.value,
                url=url,
                data=data,
                json=json_data,
                params=params,
                headers=request_headers,
                timeout=timeout,
            )

            return self._validate_response(response, expected_status)

        except Exception as e:
            self._logger.error(f"API request failed: {str(e)}")
            raise APIConnectionError(f"Failed to make API request: {str(e)}") from e

    def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        expected_status: int = 200,
    ) -> Response:
        """
        Make GET request.
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            headers: Request headers
            expected_status: Expected status code
            
        Returns:
            Response object
        """
        return self.request(
            HTTPMethod.GET,
            endpoint,
            params=params,
            headers=headers,
            expected_status=expected_status,
        )

    def post(
        self,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        expected_status: int = 201,
    ) -> Response:
        """
        Make POST request.
        
        Args:
            endpoint: API endpoint
            json_data: JSON body
            data: Form data
            headers: Request headers
            expected_status: Expected status code
            
        Returns:
            Response object
        """
        return self.request(
            HTTPMethod.POST,
            endpoint,
            json_data=json_data,
            data=data,
            headers=headers,
            expected_status=expected_status,
        )

    def put(
        self,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        expected_status: int = 200,
    ) -> Response:
        """
        Make PUT request.
        
        Args:
            endpoint: API endpoint
            json_data: JSON body
            headers: Request headers
            expected_status: Expected status code
            
        Returns:
            Response object
        """
        return self.request(
            HTTPMethod.PUT,
            endpoint,
            json_data=json_data,
            headers=headers,
            expected_status=expected_status,
        )

    def patch(
        self,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        expected_status: int = 200,
    ) -> Response:
        """
        Make PATCH request.
        
        Args:
            endpoint: API endpoint
            json_data: JSON body
            headers: Request headers
            expected_status: Expected status code
            
        Returns:
            Response object
        """
        return self.request(
            HTTPMethod.PATCH,
            endpoint,
            json_data=json_data,
            headers=headers,
            expected_status=expected_status,
        )

    def delete(
        self,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None,
        expected_status: int = 204,
    ) -> Response:
        """
        Make DELETE request.
        
        Args:
            endpoint: API endpoint
            headers: Request headers
            expected_status: Expected status code
            
        Returns:
            Response object
        """
        return self.request(
            HTTPMethod.DELETE,
            endpoint,
            headers=headers,
            expected_status=expected_status,
        )

    def _build_url(self, endpoint: str) -> str:
        """Build full URL from base URL and endpoint."""
        if endpoint.startswith("http"):
            return endpoint
        return f"{self.base_url}{endpoint}"

    def _build_headers(self, additional_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Build request headers by merging defaults and additional headers."""
        headers = self.default_headers.copy()
        if additional_headers:
            headers.update(additional_headers)
        return headers

    def _validate_response(self, response: Response, expected_status: int) -> Response:
        """
        Validate response status code.
        
        Args:
            response: Response object
            expected_status: Expected status code
            
        Returns:
            Response object
            
        Raises:
            APIResponseError: If status code doesn't match
        """
        if response.status_code != expected_status:
            self._logger.error(
                f"Unexpected status code: {response.status_code} (expected {expected_status}). "
                f"Response: {response.text[:200]}"
            )
            raise APIResponseError(
                f"Status {response.status_code} (expected {expected_status}): {response.text[:200]}"
            )

        self._logger.debug(f"Response status: {response.status_code}")
        return response

    def parse_json_response(self, response: Response) -> Dict[str, Any]:
        """
        Parse JSON response.
        
        Args:
            response: Response object
            
        Returns:
            Parsed JSON dictionary
            
        Raises:
            APIValidationError: If JSON parsing fails
        """
        try:
            data = response.json()
            self._logger.debug("Parsed JSON response")
            return data
        except json.JSONDecodeError as e:
            self._logger.error(f"Failed to parse JSON response: {str(e)}")
            raise APIValidationError(f"Invalid JSON response: {str(e)}") from e

    def close(self) -> None:
        """Close session."""
        if self.session:
            self.session.close()
            self._logger.debug("Closed API session")
        super().close()
