import json
import numpy as np
from typing import List, Dict, Set
from sklearn.metrics.pairwise import cosine_distances
import ollama

from model import Participant, DistanceWeights

with open("participants.json", "r", encoding="utf-8") as f:
    data = json.load(f)
    participants: List[Participant] = [Participant(**item) for item in data]

def get_embedding(i: int, field: str, text: str) -> List[float]:
    if not text or text.strip() == "":
        return [0.0] * 1024
    print(f'embedding participant {i} {field}: {text}')
    response = ollama.embeddings(model="snowflake-arctic-embed2:latest", prompt=text)
    return response["embedding"]

def get_field_text(p: Participant, field: str) -> str:
    value = getattr(p, field)
    if value is None:
        return ""
    if isinstance(value, list):
        return ", ".join(str(v) for v in value if v)
    return str(value)

fields = ["location", "roles", "skills", "having", "looking_for", "experience", "interests", "idea"]

embeddings: Dict[str, List[List[float]]] = {}

for field in fields:
    texts = [get_field_text(p, field) for p in participants]
    embeddings[field] = [get_embedding(i, field, text) for i, text in enumerate(texts)]

n = len(participants)
all_distances: Dict[str, np.ndarray] = {}

for field_a in fields:
    for field_b in fields:
        key = f"{field_a}_{field_b}"
        if hasattr(DistanceWeights, key):
            dist_matrix = np.zeros((n, n))
            for i in range(n):
                for j in range(n):
                    a_vec = embeddings[field_a][i]
                    b_vec = embeddings[field_b][j]
                    dist_matrix[i][j] = cosine_distances([a_vec], [b_vec])[0][0]
            all_distances[key] = dist_matrix

normalized_parts: Dict[str, np.ndarray] = {}
for key, dist_matrix in all_distances.items():
    mi, ma = dist_matrix.min(), dist_matrix.max()
    if ma - mi == 0:
        normalized_parts[key] = np.zeros_like(dist_matrix)
    else:
        normalized_parts[key] = (dist_matrix - mi) / (ma - mi)

compatibility = np.zeros((n, n))

for key in normalized_parts:
    weight = getattr(DistanceWeights, key)
    compatibility += weight * normalized_parts[key]

for i, p1 in enumerate(participants):
    for j, p2 in enumerate(participants):
        if i == j:
            continue
        reactions = p1.reactions or []
        if p2.id in reactions:
            compatibility[i][j] += DistanceWeights.reactions

compatibility_list = []
for i in range(n):
    for j in range(i + 1, n):
        compatibility_list.append({
            "user1_id": participants[i].id,
            "user2_id": participants[j].id,
            "compatibility": float(compatibility[i][j])
        })

with open("compatibility.json", "w", encoding="utf-8") as f:
    json.dump(compatibility_list, f, indent=2, ensure_ascii=False)