class Solution {
    public String[] createGrid(int m, int n) {
        String[] answer = new String[m];
        for (int i = 0; i < m; i++) {
            String row = "";
            for (int j = 0; j < n; j++) {
                if (j == 0 || i == m - 1) {
                    row += ".";
                } else {
                    row += "#";
                }
            }
            answer[i] = row;
        }
        return answer;
    }
}