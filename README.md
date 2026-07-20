# 🎵 Music Recommender Simulation

## How The System Works

This is a content-based recommender: it scores each song by how well the song's own attributes match a user's stated taste. It uses no data about other listeners, but only the song features and the user's preferences.

### What each `Song` uses

Every song carries two kinds of features:

- **Categorical** (compared by exact or explicitly defined related matches):
  `genre`, `mood`
- **Numeric 0–1** (compared by closeness): `energy`, `valence`,
  `danceability`, `acousticness` — plus `tempo_bpm` on its own scale
  (60–160)

The main recommendation score uses **genre, mood, and energy**. Acousticness
and the other numeric fields can be used for experiments or tie-breaking.

### What the `UserProfile` stores

- `favorite_genre` and `favorite_mood` : the taste labels to match
- `target_energy` : the desired energy level (may be left blank; see below)
- `likes_acoustic` : an optional preference used only as a tie-breaker

### How a score is computed (the Scoring Rule)

Each song receives a raw score from **0.0 to 4.5**:

```text
total_score = genre_score + mood_score + energy_score
```

| Feature | Exact match | Related match | Maximum |
| --- | ---: | ---: | ---: |
| `genre` | 2.00 | 0.75 | 2.00 |
| `mood` | 1.00 | 0.40 | 1.00 |
| `energy` | Calculated by distance | — | 1.50 |

The complete scoring formula is:

```text
genre_score = 2.00  if song.genre = favorite_genre
              0.75  if both genres are in the same related group
              0.00  otherwise

mood_score  = 1.00  if song.mood = favorite_mood
              0.40  if both moods are in the same related group
              0.00  otherwise

energy_difference = |song.energy - target_energy|
energy_score = 1.50 × max(0, 1 - energy_difference / 0.50)

total_score = genre_score + mood_score + energy_score
catalog_match_score = round(total_score / 4.50 × 100)
```

Therefore:

```text
0.00 ≤ total_score ≤ 4.50
0 ≤ catalog_match_score ≤ 100
```

Genre is the strongest individual signal. Mood and energy together carry more
weight than genre alone, preventing genre from dominating every result. Related
genres or moods receive limited partial credit; unrelated values receive zero.

Related matches use the following fixed, non-overlapping groups. Two different
labels receive partial credit only when they appear in the same group. An exact
label match always receives full credit.

| Genre group | Labels |
| --- | --- |
| Pop | `pop`, `indie pop` |
| Electronic | `synthwave`, `edm` |
| Calm/instrumental | `ambient`, `lofi`, `classical`, `jazz` |
| Roots | `folk`, `country`, `blues` |
| Rhythm and soul | `hip hop`, `funk`, `soul`, `reggae` |
| Heavy guitar | `rock`, `metal` |

| Mood group | Labels |
| --- | --- |
| Positive | `happy`, `hopeful`, `playful`, `euphoric` |
| Calm | `chill`, `relaxed`, `focused`, `dreamy` |
| Reflective | `moody`, `nostalgic`, `melancholy`, `sad` |
| High-drive | `energetic`, `intense`, `angry` |
| Romantic | `romantic` |

Energy rewards closeness to the user's target in either direction. The formula
above produces the following values:

| Energy difference | Energy points |
| ---: | ---: |
| 0.00 | 1.50 |
| 0.10 | 1.20 |
| 0.20 | 0.90 |
| 0.30 | 0.60 |
| 0.40 | 0.30 |
| 0.50 or more | 0.00 |

The absolute difference makes the calculation symmetric: a song that is too
mellow is penalized exactly like one that is too intense.

The resulting catalog match score describes relative fit within this small
catalog. It is not a probability, a measured prediction accuracy, or an
objective measure of song quality.

### Handling "I don't have a sense of my energy level"

A raw number like `target_energy = 0.80` is not intuitive. The interface asks
the user for a level from 1 to 5 and maps it to representative values from the
catalog's actual energy range (`0.28–0.98`):

| User selection | Stored target |
| ---: | ---: |
| 1 | 0.30 |
| 2 | 0.40 |
| 3 | 0.55 |
| 4 | 0.80 |
| 5 | 0.95 |

If the user skips energy, drop its term and use the active maximum of 3.0:

```text
catalog_match_score = round((genre_score + mood_score) / 3.0 × 100)
```

### Acousticness tie-breaking

`acousticness` does not add points to the main score. It is consulted only
when two songs have the same total score:

```text
likes_acoustic = true  → prefer higher acousticness
likes_acoustic = false → prefer lower acousticness
```

If the user does not provide this preference, the recommender preserves the
catalog order when breaking a tie.

### Potential biases

- Labels that listeners consider similar may still receive no partial credit if
  they are not placed in the same predefined group.

- The fixed related-match groups reflect the designers' interpretation of
  musical similarity. A user may understand those relationships differently.

- Energy differences of 0.50 or greater all receive zero energy points, so the
  formula cannot distinguish among songs beyond that cutoff.

- The catalog contains only 20 songs, with more examples for some genres and
  moods than others. The recommendation score therefore measures fit only
  within this limited catalog.

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

Running `python -m src.main` with the default
`genre=pop, mood=happy, energy=0.80` profile produces:

```text
====================================================
MUSIC RECOMMENDATIONS
====================================================
Loaded songs : 20
User profile : genre=pop, mood=happy, energy=0.80
Showing top 5 results
----------------------------------------------------

1. Sunrise City — Neon Echo
   Score: 4.44 / 4.50
   Reasons:
     - genre match (+2.0)
     - mood match (+1.0)
     - energy difference 0.02 (+1.44)

2. Rooftop Lights — Indigo Parade
   Score: 3.13 / 4.50
   Reasons:
     - related genre match (+0.75)
     - mood match (+1.0)
     - energy difference 0.04 (+1.38)

3. Gym Hero — Max Pulse
   Score: 3.11 / 4.50
   Reasons:
     - genre match (+2.0)
     - mood mismatch (+0.0)
     - energy difference 0.13 (+1.11)

4. Bassment Party — Groove Machine
   Score: 1.90 / 4.50
   Reasons:
     - genre mismatch (+0.0)
     - related mood match (+0.4)
     - energy difference 0.00 (+1.50)

5. Neon Horizon — Pulsewave
   Score: 1.45 / 4.50
   Reasons:
     - genre mismatch (+0.0)
     - related mood match (+0.4)
     - energy difference 0.15 (+1.05)

====================================================
```

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
