# Part C: how the program works

## Run the code

From the main project folder, run:

```sh
python3 part_c/solver.py
python3 part_c/check_solver.py
```

The code uses Python 3.12.0 and only the standard library. No extra packages are needed for Part C. The output is in English. Important code comments are in Russian.

## 1. Read the map and floor rules

`load_rules()` reads `data/maps.json`. This file stores both maps, the rewards, the ice probabilities, the discount, and the limits. The solver does not need new code for sand and water.

A state is a position, such as `(3, 1)`. Rows and columns start at 1. The wall is not a state. Goal and hole are terminal states. The game stops when it enters one of them.

## 2. Build the transition model

`move()` checks one direction. If the robot would leave the map or enter the wall, it stays in place.

`transitions()` gives the possible results of an action. Each result has a probability, a new state, a reward, and a terminal flag. On ice, the chosen direction has probability 0.8. Each side direction has probability 0.1. The program checks walls and boundaries for each result. Entering ice from ordinary floor is still a certain move. Slipping happens when leaving ice.

The reward comes from the tile where the move ends. A blocked move still has a cost. Entering the goal gives only +10. Entering a hole gives -10. After the game ends, the model stays in the terminal state and gives no more reward.

`build_model()` stores these results for every state and action. `validate_model()` checks them before the solver runs.

## 3. Calculate values

`action_value()` calculates the average reward plus the discounted future value for one action. The discount is 0.9. A reward further in the future has less weight.

`update_values()` tries all four actions and keeps the largest value. It writes a new dictionary. It does not change the old values during a round. This is important for V1 and V2.

`solve()` starts with V0 = 0. It keeps V1 and V2. It then repeats the update until the largest change is below 0.000001. It stops after at most 10,000 rounds. It reports if it did not converge.

The program prints all four V2 action calculations at the three requested positions. The student checked the handwritten Part A PDF and supplied the V1 table. It matches the program exactly, including the terminal states. The handwritten V2 results are 8 with Right, 10 with Right, and about 5.21 with Up. All three values and actions also match the program. V1 uses only one move because V0 is zero. Rewards come from the destination tile. The comparison output explains mud, ice, blocked moves, and terminal values. All supplied handwritten V1 and V2 results match. The paper and the solver stay unchanged.

## 4. Choose a policy

`extract_policy()` uses the final values. A policy chooses an action for each nonterminal state. The program compares all four action scores. Scores within 1e-12 count as ties. It chooses the first tied action in this order: Up, Right, Down, Left. Terminal states have no actions.

The value maps show numbers. The policy maps show arrows. `G`, `H`, and `#` mark the goal, hole, and wall.

## 5. Test the policy in games

`run_episode()` starts at `S`. Each game has its own `random.Random(episode_seed)`. This generator chooses a result from the transition probabilities. The policy chooses the action.

The program records the number of steps, total reward, discounted return, final state, and outcome. The first reward has weight 1. The next has weight 0.9, then 0.9 squared, and so on. The final tile decides Goal or Hole. This check happens before the step limit.

`simulate()` runs 50 games for each batch seed: 11, 22, and 33. The episode seed is `1000 * batch_seed + i`, where `i` is 0 to 49. Both maps use the same seed lists. Each game has at most 100 steps.

## 6. Check and save the results

`check_solver.py` checks the first value updates, equal action scores, discounted rewards, and the iteration limit. Small test maps check terminal outcomes on step 100 and games that reach the time limit. The checks also read the CSV files and repeat the simulations. They check the saved value and policy maps. Each chosen action must have a best score using the final values. Extra equations check the ice value and both start values. The extended route has rewards -1, -1, -3, -1, and +10. It has total reward 4 and discounted return 1.502. All saved extended games match this route.

All Part C output names start with `part_c_`. The program does not write to Part A or Part B files.

## 7. Explain the map change

On the original map, the start policy goes Right. It goes toward the ice. Ice can lead to the hole, but this route has a slightly higher expected value from the start: about 1.535824.

On the extended map, entering sand costs -2. The start action changes to Up. This route avoids sand, water, and ice. It goes through mud on the top row. Its start value is 1.502000. Mud costs -3 to enter, but the route avoids the risk at the ice.

The other chosen actions stay the same. At the water tile, the policy goes Left to ordinary floor. At the sand tile, it goes Right to ordinary floor. The cost of a tile is paid when entering it. The value at the start changes by about -0.033824. Very small differences at some other states are below the stopping tolerance.

## 8. Understand the simulations

The original map had 42, 46, and 48 goals in its three batches. The extended map had 50 goals in each batch. No game reached the time limit.

Value iteration uses all possible transitions and their probabilities. Its values describe expected discounted rewards with no fixed step limit. A batch has only 50 sampled games and a 100-step limit. Its average return can differ from the computed value. The original map has random ice moves, so its batches differ. The extended start route has no ice moves, so all its games follow the same path.

The solver uses the known rules to calculate a policy. The later games test that policy. The games do not change it.
