import csv

from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        # TODO: Implement explanation logic
        return "Explanation placeholder"

def load_songs(csv_path: str) -> List[Dict]:
    """Load songs from a CSV file and convert numeric fields."""
    songs = []

    with open(csv_path, mode="r", encoding="utf-8", newline="") as csv_file:
        reader = csv.DictReader(csv_file)

        for row in reader:
            row["id"] = int(row["id"])
            row["energy"] = float(row["energy"])
            row["tempo_bpm"] = int(row["tempo_bpm"])
            row["valence"] = float(row["valence"])
            row["danceability"] = float(row["danceability"])
            row["acousticness"] = float(row["acousticness"])
            songs.append(row)

    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Score one song against user preferences and explain each component."""
    genre_groups = (
        {"pop", "indie pop"},
        {"synthwave", "edm"},
        {"ambient", "lofi", "classical", "jazz"},
        {"folk", "country", "blues"},
        {"hip hop", "funk", "soul", "reggae"},
        {"rock", "metal"},
    )
    mood_groups = (
        {"happy", "hopeful", "playful", "euphoric"},
        {"chill", "relaxed", "focused", "dreamy"},
        {"moody", "nostalgic", "melancholy", "sad"},
        {"energetic", "intense", "angry"},
        {"romantic"},
    )

    def normalize(value: str) -> str:
        """Normalize a categorical value for comparison."""
        return value.strip().lower()

    def are_related(first: str, second: str, groups: Tuple[set, ...]) -> bool:
        """Return whether two labels belong to the same related group."""
        return any(first in group and second in group for group in groups)

    score = 0.0
    reasons = []

    preferred_genre = normalize(user_prefs["genre"])
    song_genre = normalize(song["genre"])
    if song_genre == preferred_genre:
        score += 1.0
        reasons.append("genre match (+1.0)")
    elif are_related(song_genre, preferred_genre, genre_groups):
        score += 0.375
        reasons.append("related genre match (+0.375)")
    else:
        reasons.append("genre mismatch (+0.0)")

    preferred_mood = normalize(user_prefs["mood"])
    song_mood = normalize(song["mood"])
    if song_mood == preferred_mood:
        score += 1.0
        reasons.append("mood match (+1.0)")
    elif are_related(song_mood, preferred_mood, mood_groups):
        score += 0.4
        reasons.append("related mood match (+0.4)")
    else:
        reasons.append("mood mismatch (+0.0)")

    target_energy = user_prefs.get("energy")
    if target_energy is not None:
        energy_difference = abs(float(song["energy"]) - float(target_energy))
        energy_score = 3.0 * max(0.0, 1.0 - energy_difference / 0.5)
        score += energy_score
        reasons.append(
            f"energy difference {energy_difference:.2f} (+{energy_score:.2f})"
        )
    else:
        reasons.append("energy preference not provided (not scored)")

    return round(score, 2), reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Rank all songs by score and return the top k recommendations."""
    if k <= 0:
        return []

    scored_songs = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        explanation = "; ".join(reasons)
        scored_songs.append((song, score, explanation))

    ranked_songs = sorted(
        scored_songs,
        key=lambda recommendation: recommendation[1],
        reverse=True,
    )

    return ranked_songs[:k]
