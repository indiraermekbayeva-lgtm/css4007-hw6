# Проверяем решатель независимо от сохранённых итоговых таблиц
import csv

from solver import (
    OUTPUT_DIR, action_value, build_model, extract_policy, load_rules,
    policy_map, run_episode, simulate, solve, transitions, value_map,
)


def main():
    rules = load_rules()
    checks = []
    paper = solve(rules["paper_map"], rules)
    extended = solve(rules["extended_map"], rules)

    # Эти ожидаемые значения следуют из правил, а не взяты из рукописного PDF
    expected_v1 = {
        (1, 1): -1, (1, 2): -1, (1, 3): 10, (1, 4): 0,
        (2, 1): -1, (2, 3): -1, (2, 4): 0,
        (3, 1): -1, (3, 2): -1, (3, 3): -1, (3, 4): -1,
    }
    assert paper["first_rounds"][0] == expected_v1
    for state, expected in [((1, 2), 8), ((1, 3), 10), ((2, 3), 5.21)]:
        assert abs(paper["first_rounds"][1][state] - expected) < 1e-12
    checks.append("PASS: synchronous V1 and V2 match direct calculations from the rules.")

    # Сверяем сохранённые карты и проверяем выбранное действие в каждом состоянии
    for name, solution in [("paper", paper), ("extended", extended)]:
        grid = rules[name + "_map"]
        saved_policy = (OUTPUT_DIR / f"part_c_{name}_policy.txt").read_text(encoding="utf-8")
        saved_values = (OUTPUT_DIR / f"part_c_{name}_values.txt").read_text(encoding="utf-8")
        assert saved_policy == policy_map(grid, solution["policy"]) + "\n"
        assert saved_values == value_map(grid, solution["values"]) + "\n"
        largest_residual = 0.0
        for state, action in solution["policy"].items():
            scores = [action_value(solution["model"][state][a], solution["values"], rules["discount"])
                      for a in rules["actions"]]
            chosen = action_value(solution["model"][state][action], solution["values"], rules["discount"])
            assert abs(chosen - max(scores)) <= 1e-12
            largest_residual = max(largest_residual, abs(chosen - solution["values"][state]))
        assert largest_residual < 1e-6
        checks.append(f"PASS: {name}: saved maps match; all policy actions maximize the final scores; residual={largest_residual:.12g}.")

    # Независимо вычисляем ценность льда и стартовых маршрутов по их уравнениям
    # На льду: V = 0.8 * (-1 + 0.9 * 10) + 0.1 * (-1 + 0.9 * V) + 0.1 * (-10)
    ice_value = (0.8 * 8 + 0.1 * (-1) + 0.1 * (-10)) / (1 - 0.1 * 0.9)
    paper_start = -1 + 0.9 * (-1 + 0.9 * (-1 + 0.9 * ice_value))
    extended_start = -1 + 0.9 * (-1) + 0.9 ** 2 * (-3) + 0.9 ** 3 * (-1) + 0.9 ** 4 * 10
    assert abs(paper["values"][(2, 3)] - ice_value) < 1e-6
    assert abs(paper["values"][(3, 1)] - paper_start) < 1e-6
    assert abs(extended["values"][(3, 1)] - extended_start) < 1e-6
    checks.append(f"PASS: independent policy equations: ice={ice_value:.9f}, original start={paper_start:.9f}, extended start={extended_start:.9f}.")

    # Проверяем защиту от бесконечного цикла и сообщение о несходимости
    limited_rules = dict(rules)
    limited_rules["solver"] = {"tolerance": 1e-6, "max_iterations": 1}
    limited = solve(rules["paper_map"], limited_rules)
    assert limited["iterations"] == 1 and not limited["converged"]
    for solution in [paper, extended]:
        assert solution["converged"] and solution["delta"] < 1e-6
    checks.append("PASS: convergence threshold and iteration safeguard work.")

    # На небольших тестовых картах терминальный исход важнее лимита шагов
    one_step_rules = dict(rules)
    one_step_rules["simulation"] = dict(rules["simulation"], max_steps=1)
    for grid, action, outcome, reward in [
        (["SG"], "right", "Goal", 10),
        (["SH"], "right", "Hole", -10),
        (["S."], "left", "Time limit", -1),
    ]:
        result = run_episode(grid, build_model(grid, rules), {(1, 1): action}, one_step_rules, 11000)
        assert result["outcome"] == outcome and result["steps"] == 1
        assert result["total_reward"] == reward
    checks.append("PASS: Goal and Hole on the last allowed step override Time limit.")

    # Проверяем именно шаг 100 на длинном пути и лимит при повторении состояния
    for terminal_tile, expected in [("G", "Goal"), ("H", "Hole")]:
        grid = ["S" + "." * 99 + terminal_tile]
        model = build_model(grid, rules)
        policy = {(1, column): "right" for column in range(1, 101)}
        result = run_episode(grid, model, policy, rules, 11000)
        assert result["steps"] == 100 and result["outcome"] == expected
    grid = ["S."]
    result = run_episode(grid, build_model(grid, rules), {(1, 1): "left"}, rules, 11000)
    assert result["steps"] == 100 and result["outcome"] == "Time limit"
    checks.append("PASS: exact step 100 handles Goal, Hole and Time limit correctly.")

    two_step_rules = dict(rules)
    two_step_rules["simulation"] = dict(rules["simulation"], max_steps=2)
    grid = ["S.G"]
    result = run_episode(grid, build_model(grid, rules), {(1, 1): "right", (1, 2): "right"}, two_step_rules, 11000)
    assert result["steps"] == 2 and result["total_reward"] == 9
    assert result["discounted_return"] == 8
    checks.append("PASS: discounted return is -1 + 0.9 * 10 = 8 on a two-step test.")

    # Проверяем порядок выбора при равенстве всех четырёх действий
    grid = ["S."]
    model = build_model(grid, rules)
    policy, ties = extract_policy(grid, model, {(1, 1): -10, (1, 2): -10}, rules)
    assert policy[(1, 1)] == "up" and ties[(1, 1)] == rules["actions"]
    checks.append("PASS: equal action scores choose Up first.")

    # Каждый исход скольжения отдельно проверяет границы и стены
    actual = transitions(["I#", "SG"], (1, 1), "left", rules)
    assert actual == [(0.8, (1, 1), -1, False), (0.1, (1, 1), -1, False), (0.1, (2, 1), -1, False)]
    checks.append("PASS: ice slips at a boundary keep the correct probabilities and rewards.")

    with open(OUTPUT_DIR / "part_c_episodes.csv", encoding="utf-8") as file:
        episodes = list(csv.DictReader(file))
    with open(OUTPUT_DIR / "part_c_summary.csv", encoding="utf-8") as file:
        summary = list(csv.DictReader(file))
    assert len(episodes) == 300 and len(summary) == 6
    for row in episodes:
        grid = rules[row["map"] + "_map"]
        tile = grid[int(row["final_row"]) - 1][int(row["final_column"]) - 1]
        expected_outcome = "Goal" if tile == "G" else "Hole" if tile == "H" else "Time limit"
        assert row["outcome"] == expected_outcome
        if row["map"] == "extended":
            assert int(row["steps"]) == 5 and row["outcome"] == "Goal"
            assert int(row["total_reward"]) == 4
            assert abs(float(row["discounted_return"]) - extended_start) < 1e-12
    checks.append("PASS: saved outcomes match final tiles; every extended route has 5 steps, reward 4 and discounted return 1.502.")
    for row in summary:
        batch = [episode for episode in episodes if episode["map"] == row["map"]
                 and episode["batch_seed"] == row["batch_seed"]]
        for field, outcome in [("goals", "Goal"), ("holes", "Hole"), ("time_limits", "Time limit")]:
            assert int(row[field]) == sum(episode["outcome"] == outcome for episode in batch)
        assert abs(float(row["mean_steps"]) - sum(int(e["steps"]) for e in batch) / 50) < 1e-12
        assert abs(float(row["mean_discounted_return"]) - sum(float(e["discounted_return"]) for e in batch) / 50) < 1e-12
    checks.append("PASS: CSV outcome counts and both means match the raw episode rows.")
    for name, solution in [("paper", paper), ("extended", extended)]:
        # Повторно моделируем игры и сравниваем все поля сохранённых строк
        repeated, repeated_summary = simulate(name, rules[name + "_map"], solution, rules)
        saved = [row for row in episodes if row["map"] == name]
        assert saved == [{key: str(value) for key, value in row.items()} for row in repeated]
        saved_summary = [row for row in summary if row["map"] == name]
        assert saved_summary == [{key: str(value) for key, value in row.items()} for row in repeated_summary]
        for batch_seed in [11, 22, 33]:
            batch = [row for row in saved if int(row["batch_seed"]) == batch_seed]
            assert len(batch) == 50
            assert {int(row["episode_seed"]) for row in batch} == {1000 * batch_seed + i for i in range(50)}
            assert all(1 <= int(row["steps"]) <= 100 for row in batch)
    checks.append("PASS: 300 episodes, 6 batches, correct seeds, step limits and repeatable results.")
    checks.append("PASS: all saved summaries match independently repeated simulations.")

    text = "\n".join(checks) + "\n"
    (OUTPUT_DIR / "part_c_test_results.txt").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
