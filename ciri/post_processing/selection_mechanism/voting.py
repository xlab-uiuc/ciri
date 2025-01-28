from typing import List, TypeVar, Generic

T = TypeVar('T')

class Voting(Generic[T]):
    """A class that implements voting mechanism to select most frequent elements."""
    
    def select(self, candidates: List[T]) -> List[T]:
        """
        Select the most frequent elements from the input list.
        
        Args:
            candidates: List of elements to select from
            
        Returns:
            List of elements that appear most frequently
        """
        if not candidates:
            return []
            
        # Sort to group identical elements
        sorted_candidates = sorted(candidates)
        
        max_count = 0
        most_common = []
        current_count = 1
        current_element = sorted_candidates[0]
        
        # Count frequencies and track most common elements
        for i in range(1, len(sorted_candidates)):
            if sorted_candidates[i] == current_element:
                current_count += 1
            else:
                if current_count > max_count:
                    max_count = current_count
                    most_common = [current_element]
                elif current_count == max_count:
                    most_common.append(current_element)
                    
                current_element = sorted_candidates[i]
                current_count = 1
                
        # Handle the last group
        if current_count > max_count:
            most_common = [current_element]
        elif current_count == max_count:
            most_common.append(current_element)
            
        return most_common
