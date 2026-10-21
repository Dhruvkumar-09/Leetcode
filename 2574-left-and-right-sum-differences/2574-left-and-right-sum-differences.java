class Solution {
    public int[] leftRightDifference(int[] nums) {
        int n = nums.length;
        int[] answer = new int[n];
        int rightSum = 0;
        for (int num : nums) {
            rightSum += num;
        }
        int leftSum = 0;
        for (int i = 0; i < n; i++) {
            rightSum -= nums[i];
            answer[i] = Math.abs(leftSum - rightSum);
            leftSum += nums[i];
        }
        return answer;
    }
}