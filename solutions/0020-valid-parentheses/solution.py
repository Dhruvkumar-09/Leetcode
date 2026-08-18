# Difficulty: Easy
# Tags: String, Stack
# Approach: Use a stack to match opening brackets with corresponding closing brackets.
# Time: O(n)
# Space: O(n)

class Solution:
    def isValid(self, s: str) -> bool:
        stack = []
        mapping = {")": "(", "}": "{", "]": "["}
        for char in s:
            if char in mapping:
                top_element = stack.pop() if stack else '#'
                if mapping[char] != top_element:
                    return False
            else:
                stack.append(char)
        return not stack
