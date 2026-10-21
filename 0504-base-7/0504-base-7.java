class Solution {
    public String convertToBase7(int num) {
        if (num == 0) {
            return "0";
        }
        boolean negative = num < 0;
        num = Math.abs(num);
        String result = "";
        while (num > 0) {
            result = (num % 7) + result;
            num = num / 7;
        }
        if (negative) {
            result = "-" + result;
        }
        return result;
    }
}