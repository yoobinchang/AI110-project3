# 🎵 Music Recommender Simulation

## How The System Works

This is a content-based recommender: it scores each song by how well the song's own attributes match a user's stated taste. It uses no data about other listeners, but only the song features and the user's preferences.

### What each `Song` uses

Every song carries two kinds of features:
- **Categorical** (compared by exact match): `genre`, `mood`
- **Numeric 0–1** (compared by closeness): `energy`, `valence`,`danceability`, `acousticness` — plus `tempo_bpm` on its own scale (60–152)

The recommender scores on **genre, mood, energy, and acousticness**. The other numeric fields are available for experiments.

### What the `UserProfile` stores

- `favorite_genre` and `favorite_mood` — the taste labels to match
- `target_energy` — the desired energy level (may be left blank; see below)
- `likes_acoustic` — whether the user prefers an acoustic feel

### How a score is computed (the Scoring Rule)

Each feature contributes a weighted amount, and the total is normalized to a
0–1 score:

- **Categorical** (`genre`, `mood`): exact match → full points, otherwise 0.
- **Numeric** (`energy`): rewards **closeness, not higher-or-lower**, using
  `1 − |song.energy − target_energy|`. Because the gap is symmetric, a song
  that is too mellow is penalized exactly like one that is too intense.
- **Boolean** (`likes_acoustic`): rewards high `acousticness` when true, low
  when false.

The weights encode the system's theory of taste:

| Feature | Weight | Why |
| --- | --- | --- |
| `genre` | **3.0** | Strongest, most reliable taste signal |
| `energy` | **2.0** | Wide spread in the catalog → very discriminative |
| `mood` | **1.5** | More subjective; partly overlaps with energy |
| `acousticness` | **1.0** | A refinement on top of the rest |

### Handling "I don't have a sense of my energy level"

A raw number like `target_energy = 0.40` is not intuitive, so:

- **Words, not numbers:** the user picks a label —
  `calm / mellow / moderate / upbeat / intense` — which maps to
  `0.20 / 0.40 / 0.60 / 0.80 / 0.95` internally.
- **Optional:** if the user skips energy, its term is dropped and the
  remaining weights are **renormalized**, so scores stay comparable and still
  top out at 1.0.

### How songs are chosen (the Ranking Rule)

The Scoring Rule judges one song; the Ranking Rule turns that into a
recommendation list:

```
score every song  →  sort by score (high → low)  →  take the top k  →  attach the reasons
```

Keeping the two rules separate means the scoring math (the theory of taste)
can be tuned and tested on its own, while the ranking logic (sort, cut to k,
format) stays unchanged.


---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

Paste a sample of your recommender's output here as a text block so a reader can see what it produces:

```
# e.g.:
# User profile: genre=indie, mood=chill, energy=low
# Recommendations:
#   1. ...
#   2. ...
#   3. ...
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this



