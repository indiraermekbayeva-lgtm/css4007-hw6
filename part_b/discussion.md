# Part B Discussion

## What changed when slipping was enabled?

Without slipping, the fixed policy reached the goal in all 150 games. Each batch had 50 goals and a success rate of 100%. Every game took 6 steps.

With slipping, the fixed policy reached the goal only 5 times out of 150 games. The three batches had 3, 2, and 0 goals. Their success rates were 6%, 4%, and 0%. A chosen action could move the robot in a different direction, so the same fixed route was no longer reliable.

The random policy had 1 goal out of 150 games without slipping. It had no goals in 150 games with slipping. These results show very little success in both modes. They do not prove that the random policy can never reach the goal with slipping.

All other games ended in holes. No game reached the time limit. The mean steps for the fixed policy with slipping were 4.52, 5.06, and 4.06. Shorter games did not mean better results, because most ended in holes. For the random policy, the mean steps were 8.14, 7.56, and 6.88 without slipping, and 8.06, 7.60, and 7.98 with slipping.

## How consistent were the three batches?

The fixed policy without slipping gave exactly the same results in all three batches: 50 goals and a mean of 6 steps.

With slipping, the fixed policy had different goal counts: 3, 2, and 0. However, all three batches had low success rates. The random policy also had low success in every batch. Without slipping, its goal counts were 0, 1, and 0. With slipping, all three counts were 0. Each batch contained 50 games.

## Why is one successful episode insufficient evidence?

One successful game only shows that the goal was reached once. It does not show how often the policy succeeds. For example, the random policy without slipping had one successful game, but the other 149 games failed. Many games and several batches give a clearer picture than one example.

## Why are these fixed-policy simulations not training?

The fixed policy was chosen before the games started. Its actions stayed the same in every game. Rewards were recorded, but they were not used to change the policy. The program tested the policy instead of learning a new one. The random policy did not learn either.

## What happened in the successful and failed traces?

Both saved examples in `traces.txt` used episode seed 11000 without slipping. The maps show the robot's position in square brackets after each step.

The successful example used the fixed policy. It followed the states 0, 4, 8, 9, 10, 14, and 15. It reached the goal in 6 steps and received a total reward of 1.

The failed example used the random policy. It followed the states 0, 0, 0, 1, 0, 1, and 5. Its first two actions tried to move left and up from the starting corner, so it stayed in state 0. On step 6, it moved down from state 1 into the hole at state 5. It ended with a total reward of 0.
