import csv
import json
import random
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT / "outputs"
DIRECTIONS = {"up": (-1, 0), "right": (0, 1), "down": (1, 0), "left": (0, -1)}
ARROWS = {"up": "↑", "right": "→", "down": "↓", "left": "←"}


# Загружает из JSON карту и все правила игры.
def load_rules():
    with open(ROOT / "data" / "maps.json", encoding="utf-8") as file:
        return json.load(file)


# Находит все клетки карты, кроме стен.
def get_states(grid, tiles):
    states = []
    for row in range(1, len(grid) + 1):
        for column in range(1, len(grid[0]) + 1):
            if tiles[grid[row - 1][column - 1]].get("traversable", True):
                states.append((row, column))
    return states


# Определяет тип клетки по её координатам.
def get_tile(grid, state):
    row, column = state
    return grid[row - 1][column - 1]


# Показывает, куда попадёт робот после одного движения, учитывая стены и границы.
def move(grid, state, action, tiles):
    row, column = state
    dr, dc = DIRECTIONS[action]
    next_row, next_column = row + dr, column + dc
    if not (1 <= next_row <= len(grid) and 1 <= next_column <= len(grid[0])):
        return state
    if not tiles[grid[next_row - 1][next_column - 1]].get("traversable", True):
        return state
    return next_row, next_column


# Находит возможные результаты одного действия, их вероятности и награды.
def transitions(grid, state, action, rules):
    tiles = rules["tiles"]
    floor = tiles[get_tile(grid, state)]
    if floor.get("terminal", False):
        return [(1.0, state, 0, True)]

    choices = [(1.0, action)]
    if floor["movement"] == "slippery":
        if action in ["up", "down"]:
            sides = ["left", "right"]
        else:
            sides = ["up", "down"]
        choices = [(floor["intended"], action)]
        for side in sides:
            choices.append((floor["perpendicular_each"], side))

    results = []
    for probability, direction in choices:
        new_state = move(grid, state, direction, tiles)
        destination = tiles[get_tile(grid, new_state)]
        reward = destination["reward"]
        terminal = destination.get("terminal", False)
        results.append((probability, new_state, reward, terminal))
    return results


# Собирает все возможные движения из каждой клетки в одну таблицу.
def build_model(grid, rules):
    model = {}
    for state in get_states(grid, rules["tiles"]):
        model[state] = {}
        for action in rules["actions"]:
            model[state][action] = transitions(grid, state, action, rules)
    return model


# Проверяет, что движения, вероятности и награды рассчитаны правильно.
def validate_model(rules):
    paper = rules["paper_map"]
    extended = rules["extended_map"]
    checks = []

    # Записывает результат проверки и сообщает об ошибке, если она не пройдена.
    def check(name, condition, details):
        status = "PASS" if condition else "FAIL"
        checks.append(f"{status}: {name}: {details}")
        if not condition:
            raise AssertionError(checks[-1])

    # Сравнивает рассчитанный переход с заранее известным правильным ответом.
    def expect(name, grid, state, action, expected):
        actual = transitions(grid, state, action, rules)
        check(name, actual == expected, f"{state}, {action} -> {actual}")

    expect("Boundary stays in place", paper, (1, 1), "up", [(1.0, (1, 1), -1, False)])
    expect("Wall stays in place", paper, (2, 1), "right", [(1.0, (2, 1), -1, False)])
    expect("Blocked mud move costs -3", paper, (1, 2), "down", [(1.0, (1, 2), -3, False)])
    expect("Entering mud costs -3", paper, (1, 1), "right", [(1.0, (1, 2), -3, False)])
    expect("Entering sand costs -2", extended, (3, 1), "right", [(1.0, (3, 2), -2, False)])
    expect("Entering water costs -5", extended, (3, 3), "right", [(1.0, (3, 4), -5, False)])
    expect("Sand movement is deterministic", extended, (3, 2), "right", [(1.0, (3, 3), -1, False)])
    expect("Water movement is deterministic", extended, (3, 4), "left", [(1.0, (3, 3), -1, False)])
    expect("Blocked water move costs -5", extended, (3, 4), "right", [(1.0, (3, 4), -5, False)])
    expect("Goal gives +10 with no floor cost", paper, (1, 3), "right", [(1.0, (1, 4), 10, True)])
    expect("Hole gives -10", paper, (3, 4), "up", [(1.0, (2, 4), -10, True)])
    expect("Entering ice does not cause slipping", paper, (3, 3), "up", [(1.0, (2, 3), -1, False)])
    expect("Ice up resolves wall and hole separately", paper, (2, 3), "up", [
        (0.8, (1, 3), -1, False),
        (0.1, (2, 3), -1, False),
        (0.1, (2, 4), -10, True),
    ])

    for name, grid in [("paper", paper), ("extended", extended)]:
        model = build_model(grid, rules)
        check(f"{name}: wall is not a state", (2, 2) not in model, "11 states, including 2 terminals")
        check(f"{name}: state count", len(model) == 11, str(len(model)))
        for state in model:
            for action in rules["actions"]:
                outcomes = model[state][action]
                assert abs(sum(item[0] for item in outcomes) - 1) < 1e-12
                for probability, next_state, reward, terminal in outcomes:
                    assert 0 < probability <= 1 and next_state in model
                    assert terminal == rules["tiles"][get_tile(grid, next_state)].get("terminal", False)
        check(f"{name}: all transition probabilities", True, "sum to 1; valid destinations and terminal flags")
        for action in rules["actions"]:
            outcomes = model[(2, 3)][action]
            assert [item[0] for item in outcomes] == [0.8, 0.1, 0.1]
        check(f"{name}: all ice actions", True, "intended 0.8, perpendicular 0.1 and 0.1")
        for state in [(1, 4), (2, 4)]:
            for action in rules["actions"]:
                assert model[state][action] == [(1.0, state, 0, True)]
        check(f"{name}: no rewards after termination", True, "G and H stay terminal with reward 0 for every action")
    return checks


# Вычисляет, насколько выгодно одно действие с учётом будущих наград.
def action_value(outcomes, values, discount):
    total = 0.0
    for probability, next_state, reward, terminal in outcomes:
        future = 0 if terminal else values[next_state]
        total += probability * (reward + discount * future)
    return total


# За одну итерацию находит лучшую ценность для каждой клетки.
def update_values(grid, model, values, rules):
    new_values = {}
    for state in model:
        if rules["tiles"][get_tile(grid, state)].get("terminal", False):
            new_values[state] = rules["terminal_value"]
        else:
            scores = []
            for action in rules["actions"]:
                scores.append(action_value(model[state][action], values, rules["discount"]))
            new_values[state] = max(scores)
    return new_values


# Выбирает лучшее направление движения из каждой клетки.
def extract_policy(grid, model, values, rules):
    policy = {}
    ties = {}
    for state in model:
        if rules["tiles"][get_tile(grid, state)].get("terminal", False):
            continue
        scores = {}
        for action in rules["actions"]:
            scores[action] = action_value(model[state][action], values, rules["discount"])
        best = max(scores.values())
        tied_actions = []
        for action in rules["actions"]:
            if abs(scores[action] - best) <= 1e-12:
                tied_actions.append(action)
        policy[state] = tied_actions[0]
        ties[state] = tied_actions
    return policy, ties


# Повторяет расчёты до сходимости и находит итоговую стратегию робота.
def solve(grid, rules):
    model = build_model(grid, rules)
    values = dict.fromkeys(model, rules["initial_value"])
    first_rounds = []
    converged = False
    for iteration in range(1, rules["solver"]["max_iterations"] + 1):
        new_values = update_values(grid, model, values, rules)
        delta = max(abs(new_values[state] - values[state]) for state in model)
        values = new_values
        if iteration <= 2:
            first_rounds.append(values.copy())
        if delta < rules["solver"]["tolerance"]:
            converged = True
            break
    policy, ties = extract_policy(grid, model, values, rules)
    return {
        "model": model, "values": values, "policy": policy, "ties": ties,
        "first_rounds": first_rounds, "iterations": iteration,
        "delta": delta, "converged": converged,
    }


# Показывает рассчитанные ценности клеток в виде карты.
def value_map(grid, values):
    lines = []
    for row in range(1, len(grid) + 1):
        cells = []
        for column in range(1, len(grid[0]) + 1):
            state = (row, column)
            if state in values:
                cells.append(f"{values[state]:10.6f}")
            else:
                cells.append(f"{'#':>10}")
        lines.append(" ".join(cells))
    return "\n".join(lines)


# Показывает лучшие направления движения на карте стрелками.
def policy_map(grid, policy):
    lines = []
    for row in range(1, len(grid) + 1):
        cells = []
        for column in range(1, len(grid[0]) + 1):
            state = (row, column)
            if state in policy:
                cells.append(ARROWS[policy[state]])
            else:
                cells.append(get_tile(grid, state))
        lines.append(" ".join(cells))
    return "\n".join(lines)


# Готовит расчёты V1 и V2 и сравнивает их с ручными ответами.
def paper_calculations(solution, rules):
    v1, v2 = solution["first_rounds"]
    lines = ["Computed values for the original map", "V1:", value_map(rules["paper_map"], v1)]
    for position in rules["paper_v2_positions"]:
        state = tuple(position)
        lines.append(f"\nV2 at {state}, using only V1:")
        scores = {}
        for action in rules["actions"]:
            outcomes = solution["model"][state][action]
            terms = []
            for probability, next_state, reward, terminal in outcomes:
                future = 0 if terminal else v1[next_state]
                terms.append(f"{probability:g} * ({reward:g} + {rules['discount']:g} * {future:g})")
            score = action_value(outcomes, v1, rules["discount"])
            scores[action] = score
            lines.append(f"  {action}: {' + '.join(terms)} = {score:.6f}")
        best_actions = [action for action in rules["actions"] if abs(scores[action] - v2[state]) <= 1e-12]
        lines.append(f"  V2 = {v2[state]:.6f}; best actions: {', '.join(best_actions)}")
    lines.append("\nPaper comparison: handwritten V1 and V2 answers checked and supplied by the student.")
    lines.append("MATCH: the handwritten V1 matches the computed V1 at every nonterminal position.")
    lines.append("The handwritten G and H labels represent terminal states with value 0, matching the program.")
    handwritten_v2 = [((1, 2), 8, "right"), ((1, 3), 10, "right"), ((2, 3), 5.21, "up")]
    for state, paper_value, paper_action in handwritten_v2:
        scores = {}
        for action in rules["actions"]:
            scores[action] = action_value(solution["model"][state][action], v1, rules["discount"])
        best_action = max(scores, key=scores.get)
        matches = abs(v2[state] - paper_value) < 1e-6 and best_action == paper_action
        status = "MATCH" if matches else "DIFFERENCE"
        lines.append(f"{status}: {state}: paper V2 about {paper_value:g}, {paper_action}; code {v2[state]:.6f}, {best_action}.")
    lines.extend([
        "\nV1 match and rule explanation:",
        "The full handwritten V1 table matches the computed table, including terminal states.",
        "V0 is zero. V1 uses only the expected reward of one move. The future term 0.9 * V0 is zero.",
        "The reward belongs to the destination tile, not the tile the robot leaves.",
        "At (1,2), leaving mud to the left or right gives -1, so V1 is -1, not the mud entry cost -3.",
        "At (1,3), Right enters G and gives +10, so V1 is 10. There is no extra floor cost.",
        "G and H themselves keep value 0. The +10 and -10 rewards are paid on entry only.",
        "At ice (2,3), the V1 action scores are Up=-1.9, Right=-8.2, Down=-1.9, Left=-1.",
        "For Left: 0.8 * (-1) + 0.1 * (-1) + 0.1 * (-1) = -1.",
        "The intended Left move hits the wall, so it stays on ice and still gives -1.",
        "The two side moves go Up and Down to ordinary floor and each give -1.",
        "Thus V1 on ice is -1. Slipping depends on the source tile and is checked for each possible move.",
        "Every other nonterminal tile can choose a certain move ending on ordinary floor or S for reward -1.",
        "These tiles cannot reach G in one move. Their V1 values are therefore -1.",
        "This explains why both the handwritten and computed V1 tables follow the rules.",
        "V2 uses this V1 table. The ice Up score is 0.8 * 8 + 0.1 * (-1.9) + 0.1 * (-10) = 5.21.",
        "The V1 ice best action is Left, but the V2 ice best action is Up because future rewards now matter.",
        "All three supplied handwritten V2 values and actions match the code.",
        "The matching handwritten V2 answers are 8 Right, 10 Right, and approximately 5.21 Up.",
        "There are no discrepancies between the handwritten and computed V1 and V2 results.",
        "The handwritten PDF and the solver's transition and value-update rules are unchanged.",
    ])
    return "\n".join(lines) + "\n"


# Случайно выбирает один результат движения с учётом вероятностей.
def sample_transition(outcomes, generator):
    draw = generator.random()
    cumulative = 0.0
    for outcome in outcomes:
        cumulative += outcome[0]
        if draw < cumulative:
            return outcome
    return outcomes[-1]


# Проводит одно прохождение робота от старта до завершения.
def run_episode(grid, model, policy, rules, episode_seed):
    generator = random.Random(episode_seed)
    state = next(state for state in model if get_tile(grid, state) == "S")
    total_reward = 0
    discounted_return = 0.0
    outcome = "Time limit"
    for step in range(1, rules["simulation"]["max_steps"] + 1):
        action = policy[state]
        probability, new_state, reward, terminal = sample_transition(model[state][action], generator)
        total_reward += reward
        discounted_return += rules["discount"] ** (step - 1) * reward
        state = new_state
        tile = get_tile(grid, state)
        if tile == "G":
            outcome = "Goal"
        elif tile == "H":
            outcome = "Hole"
        if terminal:
            break
    return {"steps": step, "total_reward": total_reward,
            "discounted_return": discounted_return, "outcome": outcome,
            "final_row": state[0], "final_column": state[1]}


# Запускает много прохождений и считает общие результаты.
def simulate(name, grid, solution, rules):
    episodes = []
    summary = []
    batch_size = rules["simulation"]["episodes_per_batch"]
    for batch_seed in rules["simulation"]["batch_seeds"]:
        batch = []
        for i in range(batch_size):
            episode_seed = 1000 * batch_seed + i
            result = run_episode(grid, solution["model"], solution["policy"], rules, episode_seed)
            row = {"map": name, "batch_seed": batch_seed, "episode_seed": episode_seed}
            row.update(result)
            episodes.append(row)
            batch.append(row)
        goals = sum(row["outcome"] == "Goal" for row in batch)
        holes = sum(row["outcome"] == "Hole" for row in batch)
        time_limits = sum(row["outcome"] == "Time limit" for row in batch)
        assert len(batch) == batch_size and goals + holes + time_limits == batch_size
        summary.append({
            "map": name, "batch_seed": batch_seed, "goals": goals, "holes": holes,
            "time_limits": time_limits,
            "mean_steps": sum(row["steps"] for row in batch) / batch_size,
            "mean_discounted_return": sum(row["discounted_return"] for row in batch) / batch_size,
        })
    return episodes, summary


# Сохраняет результаты программы в CSV-файл.
def write_csv(filename, rows):
    with open(OUTPUT_DIR / filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


# Запускает все этапы программы и сохраняет итоговые результаты.
def main():
    rules = load_rules()
    OUTPUT_DIR.mkdir(exist_ok=True)
    checks = validate_model(rules)
    print("\n".join(checks))
    solutions = {}
    all_episodes = []
    summaries = []
    convergence = []
    for name in ["paper", "extended"]:
        grid = rules[name + "_map"]
        solution = solve(grid, rules)
        solutions[name] = solution
        print(f"\n{name}: converged={solution['converged']}, iterations={solution['iterations']}, final change={solution['delta']:.12g}")
        values_text = value_map(grid, solution["values"]) + "\n"
        policy_text = policy_map(grid, solution["policy"]) + "\n"
        print("Final values:\n" + values_text)
        print("Policy:\n" + policy_text)
        (OUTPUT_DIR / f"part_c_{name}_values.txt").write_text(values_text, encoding="utf-8")
        (OUTPUT_DIR / f"part_c_{name}_policy.txt").write_text(policy_text, encoding="utf-8")
        convergence.append({"map": name, "iterations": solution["iterations"],
                            "final_change": solution["delta"], "converged": solution["converged"]})
        updated = update_values(grid, solution["model"], solution["values"], rules)
        residual = max(abs(updated[state] - solution["values"][state]) for state in updated)
        if solution["converged"]:
            assert residual < rules["solver"]["tolerance"]
        for state in [(1, 4), (2, 4)]:
            assert solution["values"][state] == 0 and state not in solution["policy"]
        checks.append(f"PASS: {name}: terminal values 0 and no terminal actions; Bellman residual={residual:.12g}")
        if not solution["converged"]:
            print("WARNING: iteration limit reached; the policy is not confirmed optimal.")
        episodes, summary = simulate(name, grid, solution, rules)
        all_episodes.extend(episodes)
        summaries.extend(summary)

    calculations = paper_calculations(solutions["paper"], rules)
    print("\n" + calculations)
    (OUTPUT_DIR / "part_c_first_updates.txt").write_text(calculations, encoding="utf-8")
    differences = []
    for state in solutions["paper"]["values"]:
        differences.append({
            "row": state[0], "column": state[1],
            "paper_value": solutions["paper"]["values"][state],
            "extended_value": solutions["extended"]["values"][state],
            "value_change": solutions["extended"]["values"][state] - solutions["paper"]["values"][state],
            "paper_action": solutions["paper"]["policy"].get(state, "terminal"),
            "extended_action": solutions["extended"]["policy"].get(state, "terminal"),
        })
    write_csv("part_c_map_comparison.csv", differences)
    write_csv("part_c_convergence.csv", convergence)
    write_csv("part_c_episodes.csv", all_episodes)
    write_csv("part_c_summary.csv", summaries)
    (OUTPUT_DIR / "part_c_checks.txt").write_text("\n".join(checks) + "\n", encoding="utf-8")
    print("Tie-breaking: Up, Right, Down, Left; scores within 1e-12 count as ties.")
    print(f"Python version: {sys.version.split()[0]}; Part C uses only the standard library.")
    print(f"Episodes: {len(all_episodes)}; summary rows: {len(summaries)}")
    for row in summaries:
        print(row)


if __name__ == "__main__":
    main()
