"""
Example API Endpoints - User and Auth endpoints.
Demonstrates how to create endpoints for API automation.
"""

from typing import Dict, Any, Optional

from requests import Session

from src.core.base_endpoint import BaseEndpoint
from src.core.enums import HTTPMethod


class UserEndpoint(BaseEndpoint):
    """
    User API Endpoint.
    
    Example endpoint for user-related operations.
    
    Usage:
        session = requests.Session()
        endpoint = UserEndpoint(session, "https://api.example.com")
        users = endpoint.get_all_users()
        user = endpoint.get_user(1)
        new_user = endpoint.create_user({"name": "John", "email": "john@example.com"})
    """

    def __init__(self, session: Session, base_url: str):
        """
        Initialize User Endpoint.
        
        Args:
            session: Requests Session object
            base_url: Base URL for API
        """
        super().__init__(session, base_url, endpoint_name="UserEndpoint")

    def get_all_users(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get all users.
        
        Args:
            params: Query parameters (page, limit, etc.)
            
        Returns:
            API response as dictionary
        """
        response = self.get("/users", params=params, expected_status=200)
        return self.parse_json_response(response)

    def get_user(self, user_id: int) -> Dict[str, Any]:
        """
        Get user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            User data
        """
        response = self.get(f"/users/{user_id}", expected_status=200)
        return self.parse_json_response(response)

    def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create new user.
        
        Args:
            user_data: User data (name, email, etc.)
            
        Returns:
            Created user data
        """
        response = self.post("/users", json_data=user_data, expected_status=201)
        return self.parse_json_response(response)

    def update_user(self, user_id: int, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update user.
        
        Args:
            user_id: User ID
            user_data: Updated user data
            
        Returns:
            Updated user data
        """
        response = self.put(f"/users/{user_id}", json_data=user_data, expected_status=200)
        return self.parse_json_response(response)

    def delete_user(self, user_id: int) -> None:
        """
        Delete user.
        
        Args:
            user_id: User ID
        """
        self.delete(f"/users/{user_id}", expected_status=204)
        self._logger.info(f"User {user_id} deleted")

    def search_users(self, search_query: str) -> Dict[str, Any]:
        """
        Search users.
        
        Args:
            search_query: Search query string
            
        Returns:
            Search results
        """
        response = self.get(
            "/users/search",
            params={"q": search_query},
            expected_status=200
        )
        return self.parse_json_response(response)


class AuthEndpoint(BaseEndpoint):
    """
    Authentication API Endpoint.
    
    Example endpoint for authentication operations.
    """

    def __init__(self, session: Session, base_url: str):
        """
        Initialize Auth Endpoint.
        
        Args:
            session: Requests Session object
            base_url: Base URL for API
        """
        super().__init__(session, base_url, endpoint_name="AuthEndpoint")

    def login(self, username: str, password: str) -> Dict[str, Any]:
        """
        Login and get authentication token.
        
        Args:
            username: Username
            password: Password
            
        Returns:
            Login response with token
        """
        credentials = {
            "username": username,
            "password": password,
        }

        response = self.post("/auth/login", json_data=credentials, expected_status=200)
        result = self.parse_json_response(response)

        # If token is in response, store it for future requests
        if "token" in result or "access_token" in result:
            token = result.get("token") or result.get("access_token")
            self.set_auth_header(token)

        return result

    def logout(self) -> None:
        """Logout and invalidate token."""
        self.post("/auth/logout", expected_status=200)
        self._logger.info("Logged out successfully")

    def register(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Register new user.
        
        Args:
            user_data: User registration data
            
        Returns:
            Registration response
        """
        response = self.post("/auth/register", json_data=user_data, expected_status=201)
        return self.parse_json_response(response)

    def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh authentication token.
        
        Args:
            refresh_token: Refresh token
            
        Returns:
            New token
        """
        response = self.post(
            "/auth/refresh",
            json_data={"refresh_token": refresh_token},
            expected_status=200
        )
        result = self.parse_json_response(response)

        if "token" in result or "access_token" in result:
            token = result.get("token") or result.get("access_token")
            self.set_auth_header(token)

        return result

    def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Verify if token is valid.
        
        Args:
            token: Token to verify
            
        Returns:
            Token verification result
        """
        headers = {"Authorization": f"Bearer {token}"}
        response = self.post("/auth/verify", headers=headers, expected_status=200)
        return self.parse_json_response(response)
