import json
import random
import numpy as np
from typing import List, Dict, Any

with open("participants.json", "r", encoding="utf-8") as f:
    participants = json.load(f)

with open("compatibility.json", "r", encoding="utf-8") as f:
    compatibility_list = json.load(f)

id_to_idx = {p["id"]: i for i, p in enumerate(participants)}
idx_to_id = {i: p["id"] for i, p in enumerate(participants)}
n = len(participants)

compatibility = np.zeros((n, n))
for item in compatibility_list:
    i = id_to_idx[item["user1_id"]]
    j = id_to_idx[item["user2_id"]]
    score = item["compatibility"]
    compatibility[i][j] = score
    compatibility[j][i] = score  # симметричная матрица

all_compatibility_scores = [item["compatibility"] for item in compatibility_list]
GLOBAL_MEAN = np.mean(all_compatibility_scores)
print(f"Общая средняя совместимость: {GLOBAL_MEAN:.4f}")

MIN_TEAM_SIZE = 3
MAX_TEAM_SIZE = 5
NUM_ITERATIONS = 20000

def create_random_teams() -> List[List[int]]:
    """Создаёт случайные команды из индексов участников (с ограничениями по размеру)."""
    indices = list(range(n))
    random.shuffle(indices)
    teams = []
    i = 0
    while i < len(indices):
        # Определяем размер команды: от MIN_TEAM_SIZE до MAX_TEAM_SIZE,
        # но не больше оставшихся участников
        max_possible = len(indices) - i
        if max_possible <= MAX_TEAM_SIZE:
            if max_possible >= MIN_TEAM_SIZE:
                team_size = max_possible
            else:
                # Если осталось меньше 3, добавляем в последнюю команду
                if teams:
                    teams[-1].extend(indices[i:])
                    break
                else:
                    team_size = max_possible  # вынужденно меньше MIN_TEAM_SIZE
        else:
            team_size = random.randint(MIN_TEAM_SIZE, MAX_TEAM_SIZE)
        teams.append(indices[i:i + team_size])
        i += team_size
    return teams

def get_team_similarity(team_indices: List[int]) -> float:
    """Возвращает среднюю совместимость внутри команды."""
    if len(team_indices) < 2:
        return 1.0
    total, count = 0.0, 0
    for i in range(len(team_indices)):
        for j in range(i + 1, len(team_indices)):
            total += compatibility[team_indices[i]][team_indices[j]]
            count += 1
    return total / count if count > 0 else 0.0

def get_variance_score(teams: List[List[int]]) -> float:
    """Возвращает среднее отклонение от GLOBAL_MEAN (целевая метрика)."""
    means = [get_team_similarity(team) for team in teams]
    return np.mean([(m - GLOBAL_MEAN) ** 2 for m in means])

def swap_member(teams: List[List[int]], from_team: int, to_team: int, member_idx: int) -> bool:
    """Пробует переместить участника из одной команды в другую с проверкой размеров."""
    if len(teams[from_team]) <= MIN_TEAM_SIZE:
        return False  # нельзя уменьшить ниже минимального
    if len(teams[to_team]) >= MAX_TEAM_SIZE:
        return False  # нельзя превысить максимум

    # Перемещаем
    member = teams[from_team].pop(member_idx)
    teams[to_team].append(member)
    return True

def optimize_teams(teams: List[List[int]], iterations: int) -> List[List[int]]:
    """Оптимизирует команды, пытаясь выровнять среднюю совместимость с GLOBAL_MEAN."""
    current_variance = get_variance_score(teams)
    print(f"Начальная дисперсия отклонений: {current_variance:.6f}")

    for step in range(iterations):
        # Выбираем две случайные разные команды
        if len(teams) < 2:
            break
        team_a_idx = random.randint(0, len(teams) - 1)
        team_b_idx = random.randint(0, len(teams) - 1)
        if team_a_idx == team_b_idx:
            continue

        team_a = teams[team_a_idx]
        team_b = teams[team_b_idx]

        if len(team_a) <= MIN_TEAM_SIZE or len(team_b) >= MAX_TEAM_SIZE:
            continue

        # Выбираем случайного участника из команды A
        member_idx = random.randint(0, len(team_a) - 1)
        member = team_a[member_idx]

        # Копируем текущее состояние
        new_teams = [team[:] for team in teams]
        # Перемещаем участника
        new_teams[team_b_idx].append(member)
        del new_teams[team_a_idx][member_idx]

        # Оцениваем новую дисперсию
        new_variance = get_variance_score(new_teams)

        # Принимаем изменение, если оно улучшает дисперсию
        if new_variance < current_variance:
            teams = new_teams
            current_variance = new_variance
            if step % 50 == 0:
                print(f"Итерация {step}: дисперсия улучшена до {current_variance:.6f}")

    print(f"Финальная дисперсия отклонений: {current_variance:.6f}")
    return teams

# === Основной процесс ===

# Шаг 1: Случайное распределение
teams_indices = create_random_teams()

# Шаг 2: Оптимизация
optimized_teams_indices = optimize_teams(teams_indices, NUM_ITERATIONS)

# Шаг 3: Конвертация индексов в данные участников
optimized_teams = []
for team in optimized_teams_indices:
    team_data = [participants[i] for i in team]
    optimized_teams.append(team_data)

# Шаг 4: Вывод статистики
print("\n--- Статистика по командам ---")
for i, team in enumerate(optimized_teams_indices):
    mean = get_team_similarity(team)
    print(f"Команда {i+1}: {len(team)} чел., средняя совместимость: {mean:.4f}")

# Шаг 5: Сохранение результата в формате JSON (по одной строке на участника)
output_lines = ["["]
for i, team in enumerate(optimized_teams):
    output_lines.append("  [")
    for j, member in enumerate(team):
        line = "    " + json.dumps(member, ensure_ascii=False, separators=(",", ":"))
        if j < len(team) - 1:
            line += ","
        output_lines.append(line)
    if i < len(optimized_teams) - 1:
        output_lines.append("  ],")
    else:
        output_lines.append("  ]")
output_lines.append("]")

with open("teams_balanced.json", "w", encoding="utf-8") as f:
    f.write("\n".join(output_lines))

print("\nРезультат сохранён в 'teams_balanced.json'")