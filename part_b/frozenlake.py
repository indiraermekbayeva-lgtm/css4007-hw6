# Импортируем библиотеки
import csv
import random
import gymnasium as gym
from pathlib import Path

# Создаём игру с картой 4 на 4 без скольжения
env = gym.make("FrozenLake-v1", map_name="4x4", is_slippery=False)

# Выводим карту: S — старт, F — лёд, H — лунка, G — цель
print("FrozenLake map:")
for row in env.unwrapped.desc:
    print(" ".join(cell.decode("utf-8") for cell in row))

# Задаём фиксированную стратегию для всех 11 нетерминальных состояний
# Направления: 0 — влево, 1 — вниз, 2 — вправо, 3 — вверх
FIXED_POLICY = {
    0: 1, 1: 2, 2: 1, 3: 0,
    4: 1, 6: 1, 8: 2, 9: 2,
    10: 1, 13: 2, 14: 2
}

# Выводим стратегию для проверки
print("\nFixed policy:")
for state, action in FIXED_POLICY.items():
    print(f"State {state}: action {action}")

# Закрываем среду после вывода карты
env.close()


# Создаём текстовую карту с текущим положением робота
def show_map(env, state):
    lines = []
    for row in range(4):
        cells = []
        for column in range(4):
            cell = env.unwrapped.desc[row][column].decode("utf-8")
            if row * 4 + column == state:
                cell = "[" + cell + "]"
            cells.append(cell)
        lines.append(" ".join(cells))
    return "\n".join(lines)


# Запускаем одну игру с выбранной стратегией
def run_episode(policy, episode_seed, is_slippery):
    env = gym.make("FrozenLake-v1", map_name="4x4", is_slippery=is_slippery)
    generator = random.Random(episode_seed)

    # Начинаем игру
    state, info = env.reset(seed=episode_seed)
    total_steps = 0
    total_reward = 0
    outcome = "Time limit"
    trace = ["Episode start ([ ] marks the robot position):", show_map(env, state)]

    for step in range(1, 101):
        # Выбираем действие
        if policy == "Fixed":
            action = FIXED_POLICY[state]
        else:
            action = generator.randrange(4)
        new_state, reward, terminated, truncated, info = env.step(action)

        # Считаем шаги и награды
        total_steps = step
        total_reward += reward
        trace.append(
            f"Step {step}: state {state}, action {action}, "
            f"new state {new_state}, reward {reward}"
        )
        state = new_state
        trace.append(show_map(env, state))

        # Проверяем конечную клетку перед проверкой лимита шагов
        cell = env.unwrapped.desc[state // 4][state % 4].decode("utf-8")
        if cell == "G":
            outcome = "Goal"
        elif cell == "H":
            outcome = "Hole"

        # Проверяем конец игры
        if terminated or truncated:
            break

    env.close()
    trace.append(f"Outcome: {outcome}, steps: {total_steps}, reward: {total_reward}")
    return outcome, total_steps, total_reward, trace


# Запускаем игры
output_dir = Path(__file__).resolve().parent.parent / "outputs"
output_dir.mkdir(exist_ok=True)
episodes = []
summary = []
saved_traces = {}

for is_slippery in [False, True]:
    for policy in ["Fixed", "Random"]:
        for batch_seed in [11, 22, 33]:
            batch = []
            goals = 0
            holes = 0
            time_limits = 0
            sum_steps = 0
            condition = f"slippery={is_slippery}, policy={policy}"

            for i in range(50):
                episode_seed = 1000 * batch_seed + i
                outcome, steps, total_reward, trace = run_episode(
                    policy, episode_seed, is_slippery
                )
                # Сохраняем первый тестовый эпизод, если его файла ещё нет
                if not is_slippery and policy == "Fixed" and episode_seed == 11000:
                    if not (output_dir / "trace.txt").exists():
                        with open(output_dir / "trace.txt", "w", encoding="utf-8") as file:
                            for line in trace:
                                if line.startswith("Step "):
                                    file.write(line + "\n")
                            file.write(f"Outcome: {outcome}\n")
                            file.write(f"Steps: {steps}\n")
                            file.write(f"Total reward: {total_reward}\n")

                episode = {
                    "condition": condition,
                    "batch_seed": batch_seed,
                    "episode_seed": episode_seed,
                    "policy": policy,
                    "steps": steps,
                    "total_reward": total_reward,
                    "outcome": outcome,
                }
                batch.append(episode)
                episodes.append(episode)

                # Считаем результаты
                sum_steps += steps
                if outcome == "Goal":
                    goals += 1
                    trace_type = "Successful episode"
                else:
                    trace_type = "Failed episode"
                    if outcome == "Hole":
                        holes += 1
                    else:
                        time_limits += 1

                # Сохраняем первый пример каждого исхода
                if trace_type not in saved_traces:
                    header = f"{trace_type}: {condition}, episode_seed={episode_seed}"
                    saved_traces[trace_type] = [header] + trace

            # Проверяем размер партии и сумму исходов
            assert len(batch) == 50
            assert goals + holes + time_limits == 50
            summary.append({
                "slippery": is_slippery,
                "policy": policy,
                "batch_seed": batch_seed,
                "goals": goals,
                "holes": holes,
                "time_limits": time_limits,
                "success_percent": goals / 50 * 100,
                "mean_steps": sum_steps / 50,
            })

# Сохраняем таблицы
assert len(episodes) == 600
assert len(summary) == 12
with open(output_dir / "episodes.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=[
        "condition", "batch_seed", "episode_seed", "policy",
        "steps", "total_reward", "outcome"
    ])
    writer.writeheader()
    writer.writerows(episodes)

with open(output_dir / "summary.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=[
        "slippery", "policy", "batch_seed", "goals", "holes",
        "time_limits", "success_percent", "mean_steps"
    ])
    writer.writeheader()
    writer.writerows(summary)

# Сохраняем трассировки, не изменяя первый тестовый файл
with open(output_dir / "traces.txt", "w", encoding="utf-8") as file:
    for trace_type in ["Successful episode", "Failed episode"]:
        if trace_type in saved_traces:
            file.write("\n".join(saved_traces[trace_type]) + "\n\n")
        else:
            file.write(f"{trace_type}: this outcome was not observed.\n")

# Выводим результаты для проверки
print(f"\nepisodes.csv: {len(episodes)} data rows")
print(f"summary.csv: {len(summary)} data rows")
print("slippery,policy,batch_seed,goals,holes,time_limits,success_percent,mean_steps")
for row in summary:
    print(",".join(str(value) for value in row.values()))
