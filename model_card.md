# Model Card: MoodMix 1.0

## Model Name

The model is called **MoodMix 1.0**. It recommends songs based on a user's
favorite genre, mood, and energy level.

## Goal / Task

MoodMix suggests five songs for a user. It tries to match the user's music
taste. It gives every song a score. Songs with higher scores appear first.

## Data Used

The catalog has 20 songs. Each song has a genre, mood, energy, tempo, valence,
danceability, and acousticness value. The current score only uses genre, mood,
and energy. The catalog is small. It has nine high-energy songs and only four
low-energy songs. It does not cover every genre, mood, language, or culture.

## Algorithm Summary

The model checks the song's genre, mood, and energy. An exact genre match earns
one point. A related genre earns part of a point. An exact mood match earns one
point. A related mood earns part of a point. Energy can earn up to three points.
A smaller energy gap earns more points. The model sorts the songs by total
score. It returns the top five.

## Observed Behavior / Biases

Energy has more weight than genre and mood. This can push an unrelated song
near the top. For example, "Iron Verdict" appeared in the High-Energy Pop list.
Its energy was close to the user's target. Its genre and mood were wrong. The
small catalog also gives low-energy users fewer choices. Unknown genres and
moods get no points. Tied songs stay in the order used by the CSV file.

## Evaluation Process

I tested the full 20-song catalog. I used normal and conflicting profiles. I
also tried missing values, unknown labels, and invalid energy values. I checked
the top five songs for each profile. I confirmed that scores stayed between
zero and five. I also halved the genre weight and doubled the energy weight.
The new results were different. They were not always more accurate.

### Profile Comparisons

- **High-Energy Pop and Chill Lofi:** The pop list has "Sunrise City" and "Gym
  Hero." The lofi list has "Library Rain" and "Midnight Coding." The pop user
  wants high energy. The lofi user wants calm music.

- **High-Energy Pop and Intense Rock:** "Sunrise City" leads the pop list.
  "Storm Runner" leads the rock list. "Gym Hero" appears in both lists. Its
  energy is close to both targets. It matches pop, but its mood is intense.
  This is why it keeps showing up for the Happy Pop user.

- **Chill Lofi and Intense Rock:** These lists share no top-five songs. The lofi
  list has quiet songs. The rock list has loud songs. The two profiles ask for
  opposite moods and energy levels.

## Intended Use and Non-Intended Use

MoodMix shows how a simple recommender works. It can suggest songs from this small catalog.

It should not be used as a real music service.
It should not predict a person's identity or mental health.
It should not be used for important decisions. Its scores are not probabilities.

## Ideas for Improvement

- Validate missing, unknown, and invalid user inputs.
- Reduce the energy weight and add a variety rule.
- Use tempo, valence, danceability, and acousticness.
