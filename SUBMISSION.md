# HW6 submission

## AI-use declaration

Which tools did you use, and for what?

OpenAI Codex helped write and check the Part B Python code, run the experiments, check the CSV results and dependency versions, and write the discussion and this submission text. The Part B code and discussion were prepared with AI assistance. AI use for Part A has not been confirmed here.

## Setup and reproduction

Record dependency versions, installation commands and exact run commands.

Part B dependencies are recorded in [requirements.txt](requirements.txt). The installed versions in the local virtual environment match this file:

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

Commands to set up and reproduce Part B from the repository root:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python part_b/frozenlake.py
```

These are reproduction instructions, not a record of the original installation commands. The experiment was run with Python 3.12. The script creates `outputs/` and writes `episodes.csv`, `summary.csv`, and `traces.txt` there. It also saves the first test episode as `outputs/trace.txt` if that file does not already exist. Existing files in `part_b/` are preserved.

## Part A — Paper calculations

Link your scan/photo here. Include V1 for every nonterminal tile, the three requested V2 calculations, best-action arrows/ties and your explanation. Commit this part before coding.

Scan: [Part A handwritten work](part_a/Yermekbayeva_hw6_partA.pdf).

The PDF is already tracked in Git. Its calculations and completeness have not been checked in this submission review.

## Part B — FrozenLake

### Fixed policy, written before the experiments

State the action for each nonterminal state and your reasoning.

The following policy was written before the experiments and kept unchanged. Actions are 0 = Left, 1 = Down, 2 = Right, 3 = Up.

```python
FIXED_POLICY = {
    0: 1, 1: 2, 2: 1, 3: 0,
    4: 1, 6: 1, 8: 2, 9: 2,
    10: 1, 13: 2, 14: 2
}
```

The map gives a safe route without slipping: 0 → 4 → 8 → 9 → 10 → 14 → 15. The other nonterminal states also have actions leading toward this route or the goal while avoiding holes when movement is deterministic: 1 → 2 → 6 → 10, 3 → 2, and 13 → 14. Slipping can move the robot away from these planned steps.

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

Link episode rows and example traces in outputs/. Explain slipping, variation across batches and why these runs do not train a policy.

Current Part B files:

- [Code](part_b/frozenlake.py)
- [Episode rows: 600 games](outputs/episodes.csv)
- [Batch summary: 12 batches](outputs/summary.csv)
- [Successful and failed traces with text maps](outputs/traces.txt)
- [Original single-episode trace](outputs/trace.txt)
- [Discussion](part_b/discussion.md)

Without slipping, the fixed policy succeeded in all 150 games, with 6 steps per game. With slipping, its three batches had 3, 2, and 0 goals out of 50. The random policy had 0, 1, and 0 goals without slipping, and no goals with slipping. All other games ended in holes; no game reached the time limit. One successful episode does not show how often a policy succeeds. These runs are tests, not training: rewards never change the policies. The linked discussion explains the batch variation and both traces in more detail.

Result files are saved in `outputs/`, as requested. The earlier copies in `part_b/` are kept unchanged.

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

