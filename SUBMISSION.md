# HW6 submission

## AI-use declaration

I did Part A by myself without AI help.

I used OpenAI Codex for Part B. It helped me write and check the Python code, run the tests, and prepare the results and explanations.

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

### Compare code with paper

Show V1 and the requested V2 values. Explain discrepancies.

### Values, policies and convergence

Link both value/policy maps. Record iteration counts, final value changes and tie-breaking rule.

### Simulation results

| Map | Batch seed | Goals /50 | Holes /50 | Time limits /50 | Mean steps | Mean discounted return |
| --- | --- | --- | --- | --- | --- | --- |

### Explain your results

Which values/actions changed with sand and water? Where did cost and risk matter? How do simulations relate to the computed values?

### Rule checks

Show boundary/wall behavior, slip probabilities, floor rewards and terminal handling.

