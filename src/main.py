"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from .recommender import load_songs, recommend_songs


def main() -> None:
    songs = load_songs("data/songs.csv")
    # Starter example profile
    user_prefs = {"genre": "pop", "mood": "happy", "energy": 0.8}

    recommendations = recommend_songs(user_prefs, songs, k=5)

    print("\n" + "=" * 52)
    print("MUSIC RECOMMENDATIONS")
    print("=" * 52)
    print(f"Loaded songs : {len(songs)}")
    print(
        "User profile : "
        f"genre={user_prefs['genre']}, "
        f"mood={user_prefs['mood']}, "
        f"energy={user_prefs['energy']:.2f}"
    )
    print(f"Showing top {len(recommendations)} results")
    print("-" * 52)

    if not recommendations:
        print("No recommendations found.")
        return

    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"\n{rank}. {song['title']} — {song['artist']}")
        print(f"   Score: {score:.2f} / 4.50")
        print("   Reasons:")
        for reason in explanation.split("; "):
            print(f"     - {reason}")

    print("\n" + "=" * 52)


if __name__ == "__main__":
    main()
