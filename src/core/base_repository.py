"""
Base repository class for database automation.
Implements repository pattern for data access layer.
"""

from typing import Any, Dict, List, Optional

from src.core.base_client import BaseClient
from src.core.exceptions import DatabaseQueryError, DatabaseConnectionError


class BaseRepository(BaseClient):
    """
    Base class for database repositories.
    
    Provides:
    - Query execution
    - Transaction management
    - Connection handling
    - Result mapping
    
    Usage:
        class UserRepository(BaseRepository):
            def __init__(self, session: Session):
                super().__init__(client_name="UserRepository")
                self.session = session
                
            def get_user_by_id(self, user_id: int) -> dict:
                query = "SELECT * FROM users WHERE id = %s"
                return self.execute_query(query, (user_id,))
    """

    def __init__(self, connection: Optional[Any] = None, repository_name: str = "BaseRepository"):
        """
        Initialize repository.
        
        Args:
            connection: Database connection/session object
            repository_name: Name of repository for logging
        """
        super().__init__(client_name=repository_name)
        self.connection = connection
        self._is_initialized = connection is not None

    def execute_query(
        self,
        query: str,
        params: Optional[tuple] = None,
        fetch_one: bool = False,
        timeout: int = 30,
    ) -> Any:
        """
        Execute SQL query.
        
        Args:
            query: SQL query string
            params: Query parameters (for parameterized queries)
            fetch_one: If True, return single row; if False, return all rows
            timeout: Query timeout (seconds)
            
        Returns:
            Query result (dict, list of dicts, or None)
            
        Raises:
            DatabaseConnectionError: If connection fails
            DatabaseQueryError: If query fails
        """
        try:
            if not self.connection:
                raise DatabaseConnectionError("Database connection not established")

            self._logger.debug(f"Executing query: {query[:100]}... with params: {params}")

            cursor = self.connection.cursor()
            cursor.execute(query, params or ())

            if fetch_one:
                result = cursor.fetchone()
            else:
                result = cursor.fetchall()

            cursor.close()

            self._logger.debug(f"Query executed successfully. Result rows: {len(result) if isinstance(result, list) else 1}")
            return result

        except DatabaseConnectionError:
            raise
        except Exception as e:
            self._logger.error(f"Failed to execute query: {str(e)}")
            raise DatabaseQueryError(f"Query execution failed: {str(e)}") from e

    def execute_update(
        self,
        query: str,
        params: Optional[tuple] = None,
        timeout: int = 30,
    ) -> int:
        """
        Execute UPDATE/INSERT/DELETE query.
        
        Args:
            query: SQL query string
            params: Query parameters
            timeout: Query timeout (seconds)
            
        Returns:
            Number of affected rows
            
        Raises:
            DatabaseQueryError: If query fails
        """
        try:
            if not self.connection:
                raise DatabaseConnectionError("Database connection not established")

            self._logger.debug(f"Executing update: {query[:100]}... with params: {params}")

            cursor = self.connection.cursor()
            cursor.execute(query, params or ())
            affected_rows = cursor.rowcount

            self.connection.commit()
            cursor.close()

            self._logger.debug(f"Update executed. Affected rows: {affected_rows}")
            return affected_rows

        except DatabaseConnectionError:
            raise
        except Exception as e:
            self.connection.rollback()
            self._logger.error(f"Failed to execute update: {str(e)}")
            raise DatabaseQueryError(f"Update execution failed: {str(e)}") from e

    def execute_transaction(
        self,
        operations: List[tuple],
        timeout: int = 30,
    ) -> None:
        """
        Execute multiple operations in a transaction.
        
        Args:
            operations: List of (query, params) tuples
            timeout: Transaction timeout (seconds)
            
        Raises:
            DatabaseQueryError: If transaction fails
        """
        try:
            if not self.connection:
                raise DatabaseConnectionError("Database connection not established")

            self._logger.debug(f"Starting transaction with {len(operations)} operations")

            cursor = self.connection.cursor()

            for query, params in operations:
                cursor.execute(query, params or ())

            self.connection.commit()
            cursor.close()

            self._logger.debug("Transaction completed successfully")

        except DatabaseConnectionError:
            raise
        except Exception as e:
            self.connection.rollback()
            self._logger.error(f"Transaction failed: {str(e)}")
            raise DatabaseQueryError(f"Transaction failed: {str(e)}") from e

    def close(self) -> None:
        """Close database connection."""
        if self.connection:
            self.connection.close()
            self._logger.debug("Closed database connection")
        super().close()
