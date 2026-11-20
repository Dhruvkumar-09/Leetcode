class Solution {
    public String clearDigits(String s) {
        StringBuilder result = new StringBuilder();
        for (char ch : s.toCharArray()) {
            if (Character.isDigit(ch)) {
                result.deleteCharAt(result.length() - 1);
            } else {
                result.append(ch);
            }
        }
        return result.toString();
    }
}