class Solution {
    public String removeDuplicates(String s) {
        StringBuilder result = new StringBuilder();
        for (char ch : s.toCharArray()) {
            int n = result.length();
            if (n > 0 && result.charAt(n - 1) == ch) {
                result.deleteCharAt(n - 1);
            } else {
                result.append(ch);
            }
        }
        return result.toString();
    }
}