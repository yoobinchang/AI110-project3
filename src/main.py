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

    high_energy_pop = {"genre": "pop", "mood": "happy", "energy": 0.95}
    chill_lofi = {"genre": "lofi", "mood": "chill", "energy": 0.35}
    deep_intense_rock = {"genre": "rock", "mood": "intense", "energy": 0.90}

    user_profiles = [
        ("High-Energy Pop", high_energy_pop),
        ("Chill Lofi", chill_lofi),
        ("Deep Intense Rock", deep_intense_rock),
    ]

    print("\n" + "=" * 52)
    print("CLI-FIRST MUSIC RECOMMENDATION SIMULATION")
    print("=" * 52)
    print(f"Loaded songs : {len(songs)}")

    for profile_name, user_prefs in user_profiles:
        recommendations = recommend_songs(user_prefs, songs, k=5)

        print("\n" + "-" * 52)
        print(f"PROFILE: {profile_name}")
        print(
            "Preferences: "
            f"genre={user_prefs['genre']}, "
            f"mood={user_prefs['mood']}, "
            f"energy={user_prefs['energy']:.2f}"
        )
        print(f"Showing top {len(recommendations)} results")

        if not recommendations:
            print("No recommendations found.")
            continue

        for rank, (song, score, explanation) in enumerate(recommendations, start=1):
            print(f"\n{rank}. {song['title']} — {song['artist']}")
            print(f"   Score: {score:.2f} / 5.00")
            print("   Reasons:")
            for reason in explanation.split("; "):
                print(f"     - {reason}")

    print("\n" + "=" * 52)


if __name__ == "__main__":
    main()
