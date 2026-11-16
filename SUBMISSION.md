# HW6 submission

## AI-use declaration

I did Part A by myself without AI help.

I used OpenAI Codex for Part B. It helped me write and check the Python code, run the tests, and prepare the results and explanations.

I also used OpenAI Codex for Part C. It helped write the transition model, value iteration, simulations, and checks. It ran the code and helped write the results and explanations. It also helped compare the handwritten V1 and V2 answers I supplied with the program. All supplied values and V2 actions match.

## Setup and reproduction

Part B uses the libraries in [requirements.txt](requirements.txt). Their versions in the local virtual environment are the same as in this file:

```text
cloudpickle==3.1.2
Farama-Notifications==0.0.6
gymnasium==1.4.0
numpy==2.5.5
pandas==3.1.1
python-dateutil==4.0.0
typing_extensions==4.16.0
tzdata==2026.6
```

Run these commands from the main project folder to set up and run Part B:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python part_b/frozenlake.py
```

These commands show how to run Part B again. They do not show the exact commands used for the first setup. The experiment used Python 3.12. The program creates `outputs/`. It saves `episodes.csv`, `summary.csv`, and `traces.txt` there. It also saves the first test episode in `outputs/trace.txt` if this file is missing. It keeps the old files in `part_b/`.

Part C used Python 3.12.0 and only the standard library. It needs no extra packages. The Part B library versions above stay the same.

Run Part C from the main project folder:

```sh
python3 part_c/solver.py
python3 part_c/check_solver.py
```

## Part A — Paper calculations

Scan: [Part A handwritten work](part_a/Yermekbayeva_hw6_partA.pdf).

The PDF is already saved in Git.

## Part B — FrozenLake

### Fixed policy, written before the experiments

This policy was written before the experiments. It stayed the same in all games. A policy chooses an action for each state. A state is the robot’s position on the map. Actions are 0 = Left, 1 = Down, 2 = Right, 3 = Up.

```python
FIXED_POLICY = {
    0: 1, 1: 2, 2: 1, 3: 0,
    4: 1, 6: 1, 8: 2, 9: 2,
    10: 1, 13: 2, 14: 2
}
```

The map has a safe path without slipping: 0 → 4 → 8 → 9 → 10 → 14 → 15. The other states where the game can continue also have actions. These actions lead to this path or the goal without going into holes when there is no slipping: 1 → 2 → 6 → 10, 3 → 2, and 13 → 14. When the map is slippery, the robot can move in a different direction from the chosen action.

### Results

| Slippery? | Policy | Batch seed | Goals /50 | Holes /50 | Time limits /50 | Success % | Mean steps |
| --- | --- | --- | --- | --- | --- | --- | --- |
| False | Fixed | 11 | 50 | 0 | 0 | 100.0 | 6.0 |
| False | Fixed | 22 | 50 | 0 | 0 | 100.0 | 6.0 |
| False | Fixed | 33 | 50 | 0 | 0 | 100.0 | 6.0 |
| False | Random | 11 | 0 | 50 | 0 | 0.0 | 8.14 |
| False | Random | 22 | 1 | 49 | 0 | 2.0 | 7.56 |
| False | Random | 33 | 0 | 50 | 0 | 0.0 | 6.88 |
| True | Fixed | 11 | 3 | 47 | 0 | 6.0 | 4.52 |
| True | Fixed | 22 | 2 | 48 | 0 | 4.0 | 5.06 |
| True | Fixed | 33 | 0 | 50 | 0 | 0.0 | 4.06 |
| True | Random | 11 | 0 | 50 | 0 | 0.0 | 8.06 |
| True | Random | 22 | 0 | 50 | 0 | 0.0 | 7.6 |
| True | Random | 33 | 0 | 50 | 0 | 0.0 | 7.98 |

Current Part B files:

- [Code](part_b/frozenlake.py)
- [Episode rows: 600 games](outputs/episodes.csv)
- [Batch summary: 12 batches](outputs/summary.csv)
- [Successful and failed traces with text maps](outputs/traces.txt)
- [Original single-episode trace](outputs/trace.txt)
- [Discussion](part_b/discussion.md)

An episode is one game. A batch is a group of games. A seed is a number used to make random choices repeat in the same way. Mean steps means the average number of steps in a game.

Without slipping, the fixed policy reached the goal in all 150 games. Each game took 6 steps. With slipping, its three batches had 3, 2, and 0 goals out of 50. The results changed between batches, but all three had few goals. The random policy had 0, 1, and 0 goals without slipping. It had no goals with slipping. All other games ended in holes. No game reached the time limit.

One successful episode does not show how often a policy reaches the goal. These games test the policies. They do not train them. A reward is a score from the environment after an action. The program records rewards, but it never uses them to change the policies. The discussion link gives more details about the batches and both traces. A trace shows the steps in one game.

The result files are in `outputs/`. The old copies in `part_b/` stay the same.

## Part C — Custom solver

### Code and rules

- [Solver and simulator](part_c/solver.py)
- [Extra checks](part_c/check_solver.py)
- [Step-by-step code explanation](part_c/README.md)
- [Maps and floor rules](data/maps.json)

The code reads the map and floor rules from the JSON file. The wall is not a state. A blocked move stays in place and gets the reward of that tile. Ice uses probabilities 0.8, 0.1, and 0.1 when leaving the ice tile. A move into the goal gives +10. A move into a hole gives -10. After the game ends, there are no more rewards.

### Compare code with paper

I checked my handwritten Part A PDF and supplied the V1 table below. It matches the program exactly, including the terminal states. Goal and hole values stay zero.

```text
 -1  -1  10   0
 -1   #  -1   0
 -1  -1  -1  -1
```

I supplied my handwritten V2 answers for this comparison. All three values and actions match the code. The ice value is rounded in the paper answer.

| Position | Handwritten V2 | Computed V2 | Handwritten and code action | Result |
| --- | --- | --- | --- | --- |
| (1,2) | 8 | 8.00 | Right | Match |
| (1,3) | 10 | 10.00 | Right | Match |
| (2,3) | About 5.21 | 5.21 | Up | Match |

[First updates and all V2 action calculations](outputs/part_c_first_updates.txt).

My handwritten V1 table and the computed table are the same. Both follow the rules. V0 is zero, so the future term `0.9 * V0` is zero. V1 is the best average reward from just one move. It is not a list of the rewards of the current tiles.

The reward comes from the tile where the move ends. At mud (1,2), moving Left or Right ends on ordinary floor and gives -1. So its V1 is -1. A blocked move from mud stays on mud and gives -3, but that is not the best action. At (1,3), Right enters the goal and gives +10, with no extra floor cost. So its V1 is 10. Goal and hole values stay zero. Their rewards are paid on entry, not after the game ends.

At ice (2,3), the V1 action scores are Up = -1.9, Right = -8.2, Down = -1.9, and Left = -1. For Left, the probability 0.8 move hits the wall and stays on ice. It still gives -1. The two side moves go Up and Down to ordinary floor. Each has probability 0.1 and gives -1. The average is `0.8 * (-1) + 0.1 * (-1) + 0.1 * (-1) = -1`. So V1 on ice is -1. Slipping happens when leaving ice, and each possible move must be checked for walls and boundaries.

Every other nonterminal tile can choose a certain move to ordinary floor or S for reward -1. These tiles cannot reach the goal in one move, so their V1 values are -1. All updates in a round use only the previous round. A value found in V1 must not be used to update another tile in the same round.

V2 uses the computed V1 table. At ice, Up gives `0.8 * 8 + 0.1 * (-1.9) + 0.1 * (-10) = 5.21`. The best ice action changes from Left in V1 to Up in V2 because V2 includes future rewards. Two rounds alone do not prove that the policy is final.

All supplied handwritten V1 and V2 results match the program. There are no differences in these values or in the three V2 actions. The paper PDF and the solver are unchanged.

### Values, policies and convergence

Each update uses only the values from the previous round. The initial values are zero. The discount is 0.9. The program stops when the largest value change is below 0.000001, or after 10,000 rounds. Both maps converged before the limit.

| Map | Iterations | Final largest change | Converged |
| --- | --- | --- | --- |
| paper | 12 | 2.16529310482e-07 | True |
| extended | 11 | 2.40588123201e-07 | True |

- [Original value map](outputs/part_c_paper_values.txt)
- [Original policy map](outputs/part_c_paper_policy.txt)
- [Extended value map](outputs/part_c_extended_values.txt)
- [Extended policy map](outputs/part_c_extended_policy.txt)
- [Convergence data](outputs/part_c_convergence.csv)
- [Values and actions compared by position](outputs/part_c_map_comparison.csv)

The policy uses the final values to choose the best action. Scores within 1e-12 count as ties. The first tied action is chosen in this order: Up, Right, Down, Left. The maps use arrows. Goal and hole states have no actions.

The saved maps match a new solver run. Every policy arrow chooses a best action using the final values. The largest differences between the values and one more update are about 1.95e-8 on the original map and 2.17e-8 on the extended map. Both are below 1e-6.

An extra calculation checks the policy values. On ice, the final action is Up. Its value follows `V = 0.8 * (-1 + 0.9 * 10) + 0.1 * (-1 + 0.9 * V) + 0.1 * (-10)`. The middle term is the slip into the wall, which stays on ice. This gives `V = 5.3 / 0.91`, or about 5.824176. The original start route gives `-1 + 0.9 * (-1 + 0.9 * (-1 + 0.9 * V))`, or about 1.535824. Both agree with the calculated values.

On the extended map, the start route goes Up, Up, Right, Right, Right. Its rewards are -1, -1, -3, -1, and +10. Its total reward is 4. Its discounted return is `-1 - 0.9 - 3 * 0.9^2 - 0.9^3 + 10 * 0.9^4 = 1.502`. All 150 saved extended-map games follow this route and agree with these values. Repeating the original-map games also gives the same saved results. Its batch averages can differ from the expected start value because the ice moves are random.

### Simulation results

Each map has three batches of 50 games. Batch seeds are 11, 22, and 33. The episode seed is `1000 * batch_seed + i`, for `i` from 0 to 49. Both maps use the same seeds. Each game has its own random generator and at most 100 steps. The final state decides the outcome. Goal or Hole on step 100 comes before Time limit.

Discounted return is `r0 + 0.9*r1 + 0.9^2*r2 + ...`.

| Map | Batch seed | Goals /50 | Holes /50 | Time limits /50 | Mean steps | Mean discounted return |
| --- | --- | --- | --- | --- | --- | --- |
| paper | 11 | 42 | 8 | 0 | 4.98 | 0.891260 |
| paper | 22 | 46 | 4 | 0 | 5.04 | 1.914776 |
| paper | 33 | 48 | 2 | 0 | 5.04 | 2.492144 |
| extended | 11 | 50 | 0 | 0 | 5.0 | 1.502000 |
| extended | 22 | 50 | 0 | 0 | 5.0 | 1.502000 |
| extended | 33 | 50 | 0 | 0 | 5.0 | 1.502000 |

The return means are shown to six decimal places. The CSV keeps the full values.

- [Episode results: 300 games](outputs/part_c_episodes.csv)
- [Summary: 6 batches](outputs/part_c_summary.csv)

### Explain your results

On the original map, the start action is Right. This path goes toward the ice. The ice action is Up. It has a chance of moving into the hole. The start value is about 1.535824. The three batches had 42, 46, and 48 goals. Random ice moves caused different results.

On the extended map, entering sand costs -2 and entering water costs -5. The start action changes to Up. The path avoids sand, water, and ice. It enters mud on the top row, which costs -3. This path has no random moves. All 150 games reached the goal in 5 steps. Each game had a discounted return of 1.502000.

The other chosen actions stay the same. The sand tile has action Right. The water tile has action Left. Both actions move to ordinary floor. Rewards depend on the tile entered, so a costly tile can still have a good value when the robot can leave it. The start value falls by about 0.033824. Tiny value differences at some other positions are below the stopping tolerance.

The value calculation uses all possible moves and their probabilities. It gives an expected discounted return with no fixed step limit. The simulations use only 50 games per batch and a 100-step limit. Their average returns can differ from the calculated values. The original map uses random ice moves. Its batch averages differ from the start value. The extended path has no ice, so its average matches the start value. The games test the policy and do not change it.

### Rule checks

- [Transition and reward checks](outputs/part_c_checks.txt)
- [Solver, simulation and CSV checks](outputs/part_c_test_results.txt)

All checks passed. They show that walls and boundaries keep the robot in place. Each ice action has probabilities 0.8, 0.1, and 0.1, which sum to 1. Entering ice from ordinary floor does not cause slipping. Mud, sand, and water give rewards -3, -2, and -5 when entered. Blocked moves still get the current tile reward. Entering the goal gives only +10. Goal and hole stay at value zero and give no more rewards after the game ends.

The extra checks confirm the V1 and V2 calculations from the rules, tie-breaking, the iteration safeguard, and discounted rewards. They test Goal, Hole, and Time limit on exactly step 100. They also confirm 300 episode rows, 6 summary rows, 50 games in each batch, correct seeds, and matching CSV totals. Repeated runs gave the same results.
