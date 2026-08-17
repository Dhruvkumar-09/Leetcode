# 1. Two Sum

🟢 `Easy` | [LeetCode Problem Link](https://leetcode.com/problems/two-sum/)

---

## 🏷️ Topics / Tags
`Array`, `Hash Table`

---

## 💡 Approach Summary
Iterate through the array while maintaining a hash map of `value -> index`. For each element, compute `complement = target - current_val`. If the complement exists in the map, return both indices immediately.

---

## ⏱️ Complexity Analysis

| Metric | Complexity | Explanation |
| :--- | :--- | :--- |
| **Time Complexity** | `O(n)` | Single pass through the array with average $O(1)$ hash map lookups. |
| **Space Complexity** | `O(n)` | Auxiliary hash map stores at most $n$ key-value pairs. |

---

## 💻 Solution File
- [`solution.py`](./solution.py)
