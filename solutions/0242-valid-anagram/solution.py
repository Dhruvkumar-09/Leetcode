from collections import Counter

class Solution:
    def isAnagram(self, s: str, t: str) -> bool:
        """
        Determines if t is an anagram of s using character frequency counts.
        """
        if len(s) != len(t):
            return False
        return Counter(s) == Counter(t)
