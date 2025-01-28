from typing import List, TypeVar
from ciri.post_processing.selection_mechanism.voting import Voting

T = TypeVar('T')

class Selection:
    """A class that implements selection mechanism using voting."""
    
    def __init__(self) -> None:
        """Initialize Selection with voting mechanism."""
        self.selection_mechanism = Voting()

    def select(self, candidates: List[T]) -> List[T]:
        """
        Select items from candidates using voting mechanism.
        
        Args:
            candidates: List of items to select from
            
        Returns:
            List of selected items
        """
        return self.selection_mechanism.select(candidates)
