class Solution {
    public int countCommas(int n) {
        int s=n;
        int c=0;
        while(s>999){
            s--;
            c++;
        }
      return c;
    }
}