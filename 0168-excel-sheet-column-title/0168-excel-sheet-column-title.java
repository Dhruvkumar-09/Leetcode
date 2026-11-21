class Solution {
    public String convertToTitle(int columnNumber) {
        String result = "";
        while (columnNumber > 0) {
            columnNumber--;
            char letter = (char) ('A' + columnNumber % 26);
            result = letter + result;
            columnNumber = columnNumber / 26;
        }
        return result;
    }
}