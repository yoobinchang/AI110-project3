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

## Adversarial Profile Terminal Results

The following output was produced by running the dictionary-based recommender
against the 20-song catalog. Unless noted otherwise, each profile requested
five recommendations.

### Conflicting affect (`pop`, `sad`, `0.90`)

```text
returned 5 result(s)
1. Gym Hero — Max Pulse | 3.41
2. Sunrise City — Neon Echo | 3.26
3. Rooftop Lights — Indigo Parade | 1.83
4. Storm Runner — Voltline | 1.47
5. Night Drive Loop — Neon Echo | 1.45
```

### Extreme conflict (`metal`, `sad`, `0.10`)

```text
returned 5 result(s)
1. Iron Verdict — Ashfall | 2.00
2. Empty Barroom — Cadillac Moon | 1.60
3. Winter Nocturne — Elias Farr | 1.30
4. Spacewalk Thoughts — Orbit Bloom | 0.96
5. Storm Runner — Voltline | 0.75
```

### Unknown categories (`opera`, `confused`, `0.50`)

```text
returned 5 result(s)
1. Dust Road Home — Sarah Wren | 1.50
2. Velvet Letter — June Amara | 1.44
3. Island Time — Palm Riddim | 1.35
4. Open Fields — The Willow Road | 1.35
5. Midnight Coding — LoRoom | 1.26
```

### Typo profile (`popp`, `hapy`, `0.80`)

```text
returned 5 result(s)
1. Bassment Party — Groove Machine | 1.50
2. Sunrise City — Neon Echo | 1.44
3. Rooftop Lights — Indigo Parade | 1.38
4. Night Drive Loop — Neon Echo | 1.35
5. Concrete Kings — Blockprint | 1.35
```

### Unicode look-alike (`pоp`, `happy`, `0.80`)

The `о` in `pоp` is Cyrillic rather than Latin.

```text
returned 5 result(s)
1. Sunrise City — Neon Echo | 2.44
2. Rooftop Lights — Indigo Parade | 2.38
3. Bassment Party — Groove Machine | 1.90
4. Neon Horizon — Pulsewave | 1.45
5. Night Drive Loop — Neon Echo | 1.35
```

### Blank categories (`""`, `" "`, `0.50`)

```text
returned 5 result(s)
1. Dust Road Home — Sarah Wren | 1.50
2. Velvet Letter — June Amara | 1.44
3. Island Time — Palm Riddim | 1.35
4. Open Fields — The Willow Road | 1.35
5. Midnight Coding — LoRoom | 1.26
```

### Missing energy (`pop`, `happy`)

```text
returned 5 result(s)
1. Sunrise City — Neon Echo | 3.00
2. Gym Hero — Max Pulse | 2.00
3. Rooftop Lights — Indigo Parade | 1.75
4. Neon Horizon — Pulsewave | 0.40
5. Open Fields — The Willow Road | 0.40
```

### Missing genre

```text
KeyError: 'genre'
```

### Missing mood

```text
KeyError: 'mood'
```

### Very high energy (`pop`, `happy`, `10`)

```text
returned 5 result(s)
1. Sunrise City — Neon Echo | 3.00
2. Gym Hero — Max Pulse | 2.00
3. Rooftop Lights — Indigo Parade | 1.75
4. Neon Horizon — Pulsewave | 0.40
5. Open Fields — The Willow Road | 0.40
```

### Negative energy (`pop`, `happy`, `-5`)

```text
returned 5 result(s)
1. Sunrise City — Neon Echo | 3.00
2. Gym Hero — Max Pulse | 2.00
3. Rooftop Lights — Indigo Parade | 1.75
4. Neon Horizon — Pulsewave | 0.40
5. Open Fields — The Willow Road | 0.40
```

### NaN energy (`pop`, `happy`, `"nan"`)

```text
returned 5 result(s)
1. Sunrise City — Neon Echo | 3.00
2. Gym Hero — Max Pulse | 2.00
3. Rooftop Lights — Indigo Parade | 1.75
4. Neon Horizon — Pulsewave | 0.40
5. Open Fields — The Willow Road | 0.40
```

### Infinite energy (`pop`, `happy`, `"inf"`)

```text
returned 5 result(s)
1. Sunrise City — Neon Echo | 3.00
2. Gym Hero — Max Pulse | 2.00
3. Rooftop Lights — Indigo Parade | 1.75
4. Neon Horizon — Pulsewave | 0.40
5. Open Fields — The Willow Road | 0.40
```

### Boolean energy (`pop`, `happy`, `True`)

```text
returned 5 result(s)
1. Sunrise City — Neon Echo | 3.96
2. Gym Hero — Max Pulse | 3.29
3. Rooftop Lights — Indigo Parade | 2.53
4. Neon Horizon — Pulsewave | 1.75
5. Iron Verdict — Ashfall | 1.44
```

### Numeric string (`pop`, `happy`, `"0.8"`)

```text
returned 5 result(s)
1. Sunrise City — Neon Echo | 4.44
2. Rooftop Lights — Indigo Parade | 3.13
3. Gym Hero — Max Pulse | 3.11
4. Bassment Party — Groove Machine | 1.90
5. Neon Horizon — Pulsewave | 1.45
```

### Huge numeric string (`pop`, `happy`, 5,000-digit energy)

```text
returned 5 result(s)
1. Sunrise City — Neon Echo | 3.00
2. Gym Hero — Max Pulse | 2.00
3. Rooftop Lights — Indigo Parade | 1.75
4. Neon Horizon — Pulsewave | 0.40
5. Open Fields — The Willow Road | 0.40
```

### Case and whitespace control (`" POP "`, `" Happy "`, `0.80`)

```text
returned 5 result(s)
1. Sunrise City — Neon Echo | 4.44
2. Rooftop Lights — Indigo Parade | 3.13
3. Gym Hero — Max Pulse | 3.11
4. Bassment Party — Groove Machine | 1.90
5. Neon Horizon — Pulsewave | 1.45
```

### Related-group surprise (`classical`, `chill`, `0.40`)

```text
returned 5 result(s)
1. Winter Nocturne — Elias Farr | 3.20
2. Midnight Coding — LoRoom | 3.19
3. Library Rain — Paper Lanterns | 3.10
4. Spacewalk Thoughts — Orbit Bloom | 2.89
5. Focus Flow — LoRoom | 2.65
```

### Angry but mellow (`ambient`, `angry`, `0.20`)

```text
returned 5 result(s)
1. Spacewalk Thoughts — Orbit Bloom | 3.26
2. Winter Nocturne — Elias Farr | 1.95
3. Library Rain — Paper Lanterns | 1.80
4. Coffee Shop Stories — Slow Stereo | 1.74
5. Focus Flow — LoRoom | 1.65
```

### Romantic metal (`metal`, `romantic`, `0.95`)

```text
returned 5 result(s)
1. Iron Verdict — Ashfall | 3.41
2. Storm Runner — Voltline | 2.13
3. Neon Horizon — Pulsewave | 1.50
4. Gym Hero — Max Pulse | 1.44
5. Velvet Letter — June Amara | 1.21
```

### All-zero tie (`opera`, `confused`, `10`)

```text
returned 5 result(s)
1. Sunrise City — Neon Echo | 0.00
2. Midnight Coding — LoRoom | 0.00
3. Storm Runner — Voltline | 0.00
4. Library Rain — Paper Lanterns | 0.00
5. Gym Hero — Max Pulse | 0.00
```

### Acoustic tie proxy (`likes_acoustic=True`)

```text
returned 5 result(s)
1. Sunrise City — Neon Echo | 0.00
2. Midnight Coding — LoRoom | 0.00
3. Storm Runner — Voltline | 0.00
4. Library Rain — Paper Lanterns | 0.00
5. Gym Hero — Max Pulse | 0.00
```

### Boolean result count (`k=True`)

```text
returned 1 result(s)
1. Sunrise City — Neon Echo | 4.44
```

### Fractional result count (`k=2.5`)

```text
TypeError: slice indices must be integers or None or have an __index__ method
```

### Huge result count (`k=1_000_000`)

Only the first five of the 20 returned results are displayed here.

```text
returned 20 result(s)
1. Sunrise City — Neon Echo | 4.44
2. Rooftop Lights — Indigo Parade | 3.13
3. Gym Hero — Max Pulse | 3.11
4. Bassment Party — Groove Machine | 1.90
5. Neon Horizon — Pulsewave | 1.45
```


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

I tested normal, conflicting, and invalid user profiles. One conflicting
profile asked for metal, sad music, and very low energy. The original score put
the angry, high-energy metal song "Iron Verdict" first. Its exact genre match
was strong enough to beat better mood and energy matches.

I also ran a weight-shift experiment. I cut the exact genre weight from 2.0 to
1.0. I doubled the maximum energy score from 1.5 to 3.0. The score maximum
changed from 4.5 to 5.0. The new rankings favored songs close to the target
energy. They did not always fit the requested genre or mood. For example,
"Iron Verdict" entered the High-Energy Pop top five. The change made the lists
different, but not always more accurate.

I also tested missing fields, unknown labels, invalid energy values, and unusual
values for `k`. Missing genre or mood values caused errors. Unknown labels were
silently ignored. Energy values such as `10`, `-5`, `nan`, and `inf` were
accepted but earned no energy points. Equal scores kept the order from the CSV
file.

---

## Limitations and Risks

The catalog has only 20 songs. It has more high-energy songs than low-energy
songs. This gives high-energy users more choices. The model does not understand
lyrics, language, context, or changing tastes.

Energy now supplies three of the five possible points. A song can rank highly
even when its genre and mood are wrong. This can create an energy filter bubble.
The model may keep showing similar songs instead of offering variety.

The genre and mood groups are based on the designer's choices. Some users may
not agree that the grouped labels are similar. Unsupported labels get no
credit. Tied songs favor earlier rows in the CSV file. The scores are simple
match values. They are not probabilities or measures of song quality.

---

## Reflection

My biggest learning moment was the weight-shift experiment. A small change to
the score caused unrelated songs to move into the top five. This showed me that
the weights are choices about what matters. They are not neutral facts.

AI tools helped me create test profiles and notice edge cases. They also helped
me compare the output. I still needed to run the code and check the math. AI
suggestions can sound correct even when they do not match the real output.

I was surprised that a simple point system could feel personal. A matching song
title, mood, or energy level makes the list seem thoughtful. The system does not
truly understand the listener. It only sorts numbers and labels.

If I extended the project, I would validate user input first. I would use tempo,
valence, danceability, and acousticness. I would also add a variety rule. This
would stop one energy level, genre, or artist from taking over the list.