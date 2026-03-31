"""
Example Database Repositories - User Repository.
Stub implementation for database automation.
"""

from typing import Dict, Any, Optional, List

from src.core.base_repository import BaseRepository


class UserRepository(BaseRepository):
    """
    User Repository - Data access layer for users.
    
    Example repository for user database operations.
    
    Usage:
        repo = UserRepository(db_connection)
        user = repo.get_user_by_id(1)
        users = repo.get_all_users()
        user_id = repo.create_user({"name": "John", "email": "john@example.com"})
    """

    def __init__(self, connection: Optional[Any] = None):
        """
        Initialize User Repository.
        
        Args:
            connection: Database connection
        """
        super().__init__(connection, repository_name="UserRepository")

    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            User data or None
        """
        query = "SELECT id, name, email, created_at FROM users WHERE id = %s"
        result = self.execute_query(query, (user_id,), fetch_one=True)

        if result:
            self._logger.debug(f"Found user: {user_id}")
            return dict(result)

        self._logger.warning(f"User not found: {user_id}")
        return None

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Get user by email.
        
        Args:
            email: User email
            
        Returns:
            User data or None
        """
        query = "SELECT id, name, email, created_at FROM users WHERE email = %s"
        result = self.execute_query(query, (email,), fetch_one=True)

        if result:
            self._logger.debug(f"Found user by email: {email}")
            return dict(result)

        return None

    def get_all_users(self) -> List[Dict[str, Any]]:
        """
        Get all users.
        
        Returns:
            List of user data
        """
        query = "SELECT id, name, email, created_at FROM users ORDER BY id"
        results = self.execute_query(query, fetch_one=False)

        users = [dict(row) for row in results] if results else []
        self._logger.debug(f"Retrieved {len(users)} users")
        return users

    def create_user(self, user_data: Dict[str, Any]) -> Optional[int]:
        """
        Create new user.
        
        Args:
            user_data: User data (name, email, password_hash, etc.)
            
        Returns:
            New user ID or None
        """
        name = user_data.get("name")
        email = user_data.get("email")
        password_hash = user_data.get("password_hash", "")

        query = """
            INSERT INTO users (name, email, password_hash)
            VALUES (%s, %s, %s)
            RETURNING id
        """

        result = self.execute_query(query, (name, email, password_hash), fetch_one=True)

        if result:
            user_id = result[0]
            self._logger.info(f"Created user: {user_id}")
            return user_id

        return None

    def update_user(self, user_id: int, user_data: Dict[str, Any]) -> bool:
        """
        Update user.
        
        Args:
            user_id: User ID
            user_data: Updated user data
            
        Returns:
            True if successful
        """
        updates = []
        values = []

        for key, value in user_data.items():
            if key != "id":
                updates.append(f"{key} = %s")
                values.append(value)

        if not updates:
            return False

        values.append(user_id)
        query = f"UPDATE users SET {', '.join(updates)} WHERE id = %s"

        affected_rows = self.execute_update(query, tuple(values))
        success = affected_rows > 0

        if success:
            self._logger.info(f"Updated user: {user_id}")
        else:
            self._logger.warning(f"Failed to update user: {user_id}")

        return success

    def delete_user(self, user_id: int) -> bool:
        """
        Delete user.
        
        Args:
            user_id: User ID
            
        Returns:
            True if successful
        """
        query = "DELETE FROM users WHERE id = %s"
        affected_rows = self.execute_update(query, (user_id,))

        success = affected_rows > 0

        if success:
            self._logger.info(f"Deleted user: {user_id}")
        else:
            self._logger.warning(f"Failed to delete user: {user_id}")

        return success

    def user_exists(self, user_id: int) -> bool:
        """
        Check if user exists.
        
        Args:
            user_id: User ID
            
        Returns:
            True if exists
        """
        user = self.get_user_by_id(user_id)
        return user is not None
