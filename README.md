# HackaTeams

## 🚀 Team Formation Assistant

This project is designed to **automatically form balanced and compatible teams** from a group of participants based on their profiles, interests, skills, roles, and social interactions (e.g., reactions in a chat). It uses **semantic embeddings**, **compatibility scoring**, and **team optimization algorithms** to group people into teams of 3–5 members, maximizing synergy and minimizing mismatch.

Perfect for hackathons, startup weekends, innovation labs, or any collaborative event where forming effective teams matters!

---

## 📌 Key Features

- ✅ **Participant Profile Extraction**: Parses raw messages (e.g., from Telegram) into structured user profiles using LLMs.
- ✅ **Semantic Compatibility Scoring**: Uses embeddings (`snowflake-arctic-embed2`) to compute similarity between users across multiple fields (skills, interests, ideas, etc.).
- ✅ **Reaction-Based Boosting**: Participants who received positive reactions from others get a compatibility boost.
- ✅ **Two Team Formation Strategies**:
  - `teams_balanced.py`: Balances team quality around the global average for fairness.
  - `teams_united.py`: Forms high-synergy teams by greedily grouping most compatible users.
- ✅ **Export to JSON & Excel**: Results are human- and machine-readable.

---

## 🧱 Architecture Overview

```
messages.json → participants.json → compatibility.json → teams_*.json
```

1. **Input**: Chat export with user introductions (e.g., Telegram).
2. **Profile Extraction**: LLM extracts structured data into `participants.json`.
3. **Compatibility Matrix**: Semantic distances computed via embeddings → `compatibility.json`.
4. **Team Formation**: Two algorithms generate optimal team configurations.

---

## 🛠️ Usage Guide

### 1. Prerequisites

- Python 3.10+
- Ollama running locally (for embeddings and LLM parsing)
- Installed models:
  ```bash
  ollama pull snowflake-arctic-embed2:latest
  ollama pull gpt-oss:20b
  ```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

> Ensure `pandas`, `openpyxl`, `ollama`, `scikit-learn`, and `langchain` are installed.

---

### 3. Prepare Input Data

You need a `messages.json` file containing user messages (e.g., self-introductions).  
Example format:
```json
[
  {
    "id": "user123",
    "text": "Hi! I'm Alex from Berlin. I'm a frontend dev with React and TypeScript. Looking for a PM and a designer for my AI fitness app idea..."
  },
  ...
]
```

💡 Tip: Use `messages.sh` to extract relevant messages from a Telegram export.

Edit the path in `messages.sh` and run:
```bash
bash messages.sh > messages.json
```

---

### 4. Extract Participant Profiles

Run the LLM-powered parser:

```bash
python participants.py
```

✅ Output:
- `participants.json` — structured participant data
- `participants.xlsx` — readable spreadsheet

---

### 5. Compute Compatibility Scores

```bash
python compatibility.py
```

✅ Output:
- `compatibility.json` — pairwise compatibility scores between all users

> This step uses embeddings to compute semantic similarity across fields like skills, interests, and project ideas.

---

### 6. Generate Teams

Choose one (or both) strategies:

#### A. Balanced Teams (Fair Distribution)

All teams have similar average compatibility (no super-team, no weak team):

```bash
python teams_balanced.py
```

✅ Output: `teams_balanced.json`

#### B. United Teams (High-Synergy Groups)

Maximize internal team compatibility using a greedy algorithm:

```bash
python teams_united.py
```

✅ Output: `teams_united.json`

---

## 🔍 Customization

### Adjust Compatibility Weights

Edit `model.py` → `DistanceWeights` class:

```python
class DistanceWeights:
    reactions = 0.5
    location_location = 0.5
    roles_roles = -1.0          # Penalty for same roles
    skills_skills = -1.0        # Penalty for skill overlap
    looking_for_roles = 1.0     # Reward for matching needs
    interests_interests = 1.0   # Reward shared interests
    # Add or modify weights as needed
```

> Negative weights discourage matches (e.g., same role), positive encourage.

### Change Team Size

In `teams_balanced.py` and `teams_united.py`, modify:

```python
MIN_TEAM_SIZE = 3
MAX_TEAM_SIZE = 5
```

---

## 📂 File Structure

```
.
├── messages.json            # Input: user messages
├── participants.json        # Output: parsed profiles
├── compatibility.json       # Output: pairwise compatibility
├── teams_balanced.json      # Output: fair teams
├── teams_united.json        # Output: high-synergy teams
├── participants.xlsx        # Exported spreadsheet
├── messages.sh              # Script to extract Telegram messages
├── model.py                 # Data models and weights
├── participants.py          # LLM parsing
├── compatibility.py         # Embedding & similarity
├── teams_balanced.py        # Fair team formation
├── teams_united.py          # Synergy-focused teams
└── requirements.txt         # Python dependencies
```

---

## ⚠️ Notes

- **Privacy**: Input data may contain personal info. Handle responsibly.
- **Excluded Files**: Binary and cache files (e.g., `.xlsx`, `__pycache__`) are git-ignored.
- **Model Requirements**: Requires local LLMs via Ollama for privacy and speed.
- **Language**: All input/output is in **Russian** (as per prompt in `participants.py`).

---

## 🙌 Inspiration

Built for real-world team formation challenges — where the right mix of skills, chemistry, and goals determines success.

Let’s stop random team draws and start building **intelligent collaboration**.

---

## 📬 Feedback & Contributions

Open an issue or submit a PR!  
Let’s make team formation smarter together. 💡

--- 

*Made with ❤️ and `ollama`*