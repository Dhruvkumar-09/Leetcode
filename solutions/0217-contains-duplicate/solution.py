from typing import List

class Solution:
    def containsDuplicate(self, nums: List[int]) -> bool:
        """
        Determines if any value appears at least twice in the array.
        Uses a hash set to track visited elements with early termination.
        """
        seen = set()
        for num in nums:
            if num in seen:
                return True
            seen.add(num)
        return False
