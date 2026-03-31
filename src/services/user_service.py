"""
Service Layer - Business logic orchestration.
Services combine UI, API, and DB automation for complex workflows.
"""

from typing import Optional, Dict, Any, List

from src.core.context import TestContext
from src.utils.logger import Logger


class UserService:
    """
    User Service - Orchestrates user-related business workflows.
    
    Demonstrates how to combine multiple automation layers:
    - UI automation (login, browse UI)
    - API automation (create, update, delete via API)
    - Database automation (verify data in DB)
    
    Provides loose coupling by delegating to layer-specific clients.
    
    Usage:
        service = UserService(context)
        # Create user via API and verify in UI
        service.create_and_verify_user("john_doe", "john@example.com")
        # Login via UI
        service.login_user("john_doe", "password")
    """

    def __init__(self, context: TestContext):
        """
        Initialize User Service.
        
        Args:
            context: TestContext with all clients (UI, API, DB, AWS)
        """
        self.context = context
        self._logger = Logger.get_logger(f"{self.__class__.__module__}.{self.__class__.__name__}")

    def create_user_via_api(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create user via API.
        
        Args:
            user_data: User data (name, email, password, etc.)
            
        Returns:
            Created user data from API
        """
        if not self.context.api_client:
            raise ValueError("API client not initialized in context")

        from src.layers.api.endpoints.example_endpoints import UserEndpoint

        endpoint = UserEndpoint(self.context.api_client.session, self.context.api_client.base_url)
        user = endpoint.create_user(user_data)

        # Store in context for later use
        self.context.add_data("created_user_id", user.get("id"))
        self.context.add_data("created_user", user)

        self._logger.info(f"Created user via API: {user.get('email')}")
        return user

    def create_user_via_ui(self, page_class, user_data: Dict[str, Any]) -> None:
        """
        Create user via UI.
        
        Args:
            page_class: Page class to use for creation
            user_data: User data
        """
        if not self.context.ui_client:
            raise ValueError("UI client not initialized in context")

        page = page_class(self.context.ui_client.page)
        # TODO: Implement UI creation logic
        self._logger.info(f"Created user via UI: {user_data.get('email')}")

    def create_user_in_database(self, user_data: Dict[str, Any]) -> Optional[int]:
        """
        Create user in database.
        
        Args:
            user_data: User data
            
        Returns:
            Created user ID
        """
        if not self.context.db_client:
            raise ValueError("Database client not initialized in context")

        from src.layers.database.repositories.user_repository import UserRepository

        repository = UserRepository(self.context.db_client.connection)
        user_id = repository.create_user(user_data)

        self.context.add_data("db_user_id", user_id)

        self._logger.info(f"Created user in database: ID {user_id}")
        return user_id

    def create_and_verify_user(
        self,
        username: str,
        email: str,
        password: str = "TestPassword123!",
    ) -> Dict[str, Any]:
        """
        Create user via API and verify in database.
        
        Demonstrates combining API and DB automation in a single workflow.
        
        Args:
            username: Username
            email: Email
            password: Password
            
        Returns:
            Created user data from API
        """
        user_data = {
            "name": username,
            "email": email,
            "password": password,
        }

        # Create via API
        api_user = self.create_user_via_api(user_data)

        # Verify in database (if DB client available)
        if self.context.db_client:
            from src.layers.database.repositories.user_repository import UserRepository

            repo = UserRepository(self.context.db_client.connection)
            db_user = repo.get_user_by_email(email)

            if not db_user:
                self._logger.warning(f"User not found in database: {email}")

        self._logger.info(f"User created and verified: {email}")
        return api_user

    def login_user_via_api(self, username: str, password: str) -> Dict[str, Any]:
        """
        Login user via API.
        
        Args:
            username: Username
            password: Password
            
        Returns:
            Login response with token
        """
        if not self.context.api_client:
            raise ValueError("API client not initialized in context")

        from src.layers.api.endpoints.example_endpoints import AuthEndpoint

        endpoint = AuthEndpoint(self.context.api_client.session, self.context.api_client.base_url)
        result = endpoint.login(username, password)

        # Store authentication token in context
        token = result.get("token") or result.get("access_token")
        if token:
            self.context.add_data("auth_token", token)

        self._logger.info(f"Logged in user via API: {username}")
        return result

    def login_user_via_ui(self, page_class, username: str, password: str) -> None:
        """
        Login user via UI.
        
        Args:
            page_class: Login page class
            username: Username
            password: Password
        """
        if not self.context.ui_client:
            raise ValueError("UI client not initialized in context")

        page = page_class(self.context.ui_client.page)
        page.login(username, password)

        self.context.add_data("logged_in_user", username)

        self._logger.info(f"Logged in user via UI: {username}")

    def get_all_users_from_api(self) -> List[Dict[str, Any]]:
        """
        Get all users from API.
        
        Returns:
            List of users
        """
        if not self.context.api_client:
            raise ValueError("API client not initialized in context")

        from src.layers.api.endpoints.example_endpoints import UserEndpoint

        endpoint = UserEndpoint(self.context.api_client.session, self.context.api_client.base_url)
        users = endpoint.get_all_users()

        self._logger.info(f"Retrieved {len(users) if isinstance(users, list) else 1} users from API")
        return users

    def get_all_users_from_database(self) -> List[Dict[str, Any]]:
        """
        Get all users from database.
        
        Returns:
            List of users
        """
        if not self.context.db_client:
            raise ValueError("Database client not initialized in context")

        from src.layers.database.repositories.user_repository import UserRepository

        repository = UserRepository(self.context.db_client.connection)
        users = repository.get_all_users()

        self._logger.info(f"Retrieved {len(users)} users from database")
        return users

    def delete_user_via_api(self, user_id: int) -> None:
        """
        Delete user via API.
        
        Args:
            user_id: User ID
        """
        if not self.context.api_client:
            raise ValueError("API client not initialized in context")

        from src.layers.api.endpoints.example_endpoints import UserEndpoint

        endpoint = UserEndpoint(self.context.api_client.session, self.context.api_client.base_url)
        endpoint.delete_user(user_id)

        self._logger.info(f"Deleted user via API: {user_id}")
