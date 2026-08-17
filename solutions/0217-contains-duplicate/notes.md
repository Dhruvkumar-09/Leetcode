# 217. Contains Duplicate

🟢 `Easy` | [LeetCode Problem Link](https://leetcode.com/problems/contains-duplicate/)

---

## 🏷️ Topics / Tags
`Array`, `Hash Table`, `Sorting`

---

## 💡 Approach Summary
Traverse the elements and insert each into a hash set. If an element is already present in the set, a duplicate is found and we return `True`. If traversal completes without duplicates, return `False`.

---

## ⏱️ Complexity Analysis

| Metric | Complexity | Explanation |
| :--- | :--- | :--- |
| **Time Complexity** | `O(n)` | Linear scan of the array with $O(1)$ set lookups. |
| **Space Complexity** | `O(n)` | Set stores up to $n$ unique elements in worst case. |

---

## 💻 Solution File
- [`solution.py`](./solution.py)
