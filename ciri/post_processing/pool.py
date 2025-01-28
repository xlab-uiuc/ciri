from typing import List, TypeVar, Generic

T = TypeVar('T')

class BasePool(Generic[T]):
    """A fixed-size pool implementation that stores elements of type T."""
    
    def __init__(self, max_len: int):
        """
        Initialize the pool with a maximum length.
        
        Args:
            max_len: Maximum number of elements the pool can hold
        """
        if max_len <= 0:
            raise ValueError("max_len must be positive")
            
        self.max_len = max_len
        self.pool: List[T] = []
        
    @property 
    def is_full(self) -> bool:
        """Check if pool has reached maximum capacity."""
        return len(self.pool) >= self.max_len
        
    @property
    def full_status(self) -> bool:
        """Alias for is_full property to maintain compatibility."""
        return self.is_full
        
    def add(self, item: T) -> bool:
        """
        Add an item to the pool if not full.
        
        Args:
            item: Item to add to the pool
            
        Returns:
            bool: True if item was added, False if pool is full
        """
        if self.is_full:
            return False
            
        self.pool.append(item)
        return True
