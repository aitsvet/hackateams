import json
import numpy as np
from typing import List, Dict, Set

with open("participants.json", "r", encoding="utf-8") as f:
    participants_data = json.load(f)
    participants = {p["id"]: p for p in participants_data}

with open("compatibility.json", "r", encoding="utf-8") as f:
    compatibility_list = json.load(f)

id_to_idx = {p["id"]: i for i, p in enumerate(participants_data)}
idx_to_id = {i: p["id"] for i, p in enumerate(participants_data)}
n = len(participants_data)

similarity_matrix = np.zeros((n, n))
for item in compatibility_list:
    i = id_to_idx[item["user1_id"]]
    j = id_to_idx[item["user2_id"]]
    sim = item["compatibility"]
    similarity_matrix[i][j] = sim
    similarity_matrix[j][i] = sim

MIN_TEAM_SIZE = 3
MAX_TEAM_SIZE = 5
THRESHOLD = np.percentile([item["compatibility"] for item in compatibility_list], 50)  # адаптивный порог

# Алгоритм: жадное формирование команд по максимальной средней совместимости
used: Set[int] = set()
teams: List[List[Dict]] = []

def get_avg_similarity(indices: List[int]) -> float:
    if len(indices) < 2:
        return 1.0
    total, count = 0.0, 0
    for i in indices:
        for j in indices:
            if i < j:
                total += similarity_matrix[i][j]
                count += 1
    return total / count if count > 0 else 0.0

while len(used) < n:
    if n - len(used) <= MAX_TEAM_SIZE and n - len(used) >= MIN_TEAM_SIZE:
        remaining = [i for i in range(n) if i not in used]
        team_data = [participants[idx_to_id[i]] for i in remaining]
        teams.append(team_data)
        used.update(remaining)
        break

    # Начинаем с наименее совместимого участника (чтобы не застрял)
    candidate_seeds = [i for i in range(n) if i not in used]
    if not candidate_seeds:
        break

    # Выбираем кандидата с минимальным средним с другими свободными
    avg_sims = []
    for i in candidate_seeds:
        others = [j for j in candidate_seeds if j != i]
        if not others:
            avg_sims.append(1.0)
        else:
            avg_sims.append(sum(similarity_matrix[i][j] for j in others) / len(others))
    seed_idx = candidate_seeds[np.argmin(avg_sims)]
    
    team_indices = [seed_idx]
    used.add(seed_idx)

    # Добавляем ближайших по совместимости
    candidates = [i for i in range(n) if i not in used]
    while len(team_indices) < MAX_TEAM_SIZE and candidates:
        best_score = -1
        best_candidate = -1
        for c in candidates:
            new_team = team_indices + [c]
            score = get_avg_similarity(new_team)
            if score > best_score:
                best_score = score
                best_candidate = c
        if best_score >= THRESHOLD or len(team_indices) < MIN_TEAM_SIZE:
            team_indices.append(best_candidate)
            used.add(best_candidate)
            candidates.remove(best_candidate)
        else:
            break

    # Сохраняем команду только если она достаточно большая
    if len(team_indices) >= MIN_TEAM_SIZE:
        team_data = [participants[idx_to_id[i]] for i in team_indices]
        teams.append(team_data)
    else:
        # Возвращаем участников обратно, если команда слишком мала (не идеально, но для простоты)
        used.difference_update(team_indices)

# Сохранение результата, каждый участник в команде — в одной строке
with open("teams_united.json", "w", encoding="utf-8") as f:
    # json.dump(teams, f, indent=2, ensure_ascii=False)
    # continue
    f.write("[\n")
    for i, team in enumerate(teams):
        f.write("  [\n")
        for j, member in enumerate(team):
            line = "    " + json.dumps(member, ensure_ascii=False, separators=(",", ":"))
            if j < len(team) - 1:
                line += ","
            line += "\n"
            f.write(line)
        f.write("  ]")
        if i < len(teams) - 1:
            f.write(",")
        f.write("\n")
    f.write("]\n")