import pandas as pd
from utils import records_to_json


def mood_label(energy, valence):
    if energy >= 0.6 and valence >= 0.6:
        return "Happy / Energetic"

    if energy >= 0.6 and valence < 0.6:
        return "Intense / Melancholic"

    if energy < 0.6 and valence >= 0.6:
        return "Calm / Positive"

    return "Sad / Calm"


def mood_target(mood):
    targets = {
        "Happy / Energetic": (0.80, 0.80),
        "Intense / Melancholic": (0.80, 0.30),
        "Calm / Positive": (0.30, 0.75),
        "Sad / Calm": (0.30, 0.25)
    }

    return targets.get(mood)


def points(df, limit=3000):
    result = df[
        ["track_id", "track_name", "artists", "energy", "valence"]
    ].dropna()

    if len(result) > limit:
        result = result.sample(limit, random_state=42)

    return records_to_json(result)


def songs_by_mood(df, mood, limit=50):
    result = df.copy()

    # -----------------------------------------
    # 1. Assign mood using energy + valence
    # -----------------------------------------

    result["mood"] = result.apply(
        lambda row: mood_label(
            row["energy"],
            row["valence"]
        ),
        axis=1
    )

    result = result[
        result["mood"].str.lower() == mood.lower()
    ].copy()

    if result.empty:
        return []

    # -----------------------------------------
    # 2. Remove duplicate songs
    # -----------------------------------------

    result = result.drop_duplicates(
        subset=["track_name", "artists"]
    ).copy()

    # -----------------------------------------
    # 3. Find ideal energy + valence
    #    for the selected mood
    # -----------------------------------------

    target = mood_target(mood)

    if target is None:
        return []

    target_energy, target_valence = target

    # -----------------------------------------
    # 4. Calculate mood distance
    # -----------------------------------------

    result["mood_distance"] = (
        (result["energy"] - target_energy) ** 2
        +
        (result["valence"] - target_valence) ** 2
    ) ** 0.5

    # Smaller distance = better mood match
    result = result.sort_values(
        "mood_distance",
        ascending=True
    )

    # -----------------------------------------
    # 5. Select songs across genres
    # -----------------------------------------

    genre_groups = {}

    for genre, group in result.groupby(
        "track_genre",
        dropna=False
    ):
        genre_groups[genre] = group

    selected = []

    # Number of genres we want to represent
    max_genres = min(len(genre_groups), 10)

    # Keep only the strongest genres first
    genre_order = sorted(
        genre_groups,
        key=lambda g: genre_groups[g][
            "mood_distance"
        ].mean()
    )[:max_genres]

    # -----------------------------------------
    # 6. Round-robin selection
    # -----------------------------------------

    while len(selected) < limit:

        added_this_round = False

        for genre in genre_order:

            group = genre_groups[genre]

            if group.empty:
                continue

            row = group.iloc[0]

            selected.append(row)

            genre_groups[genre] = group.iloc[1:]

            added_this_round = True

            if len(selected) >= limit:
                break

        if not added_this_round:
            break

    # -----------------------------------------
    # 7. Convert back to DataFrame
    # -----------------------------------------

    if not selected:
        return []

    result = result.iloc[0:0].copy()

    result = __import__("pandas").DataFrame(selected)

    # -----------------------------------------
    # 8. Return useful columns
    # -----------------------------------------

    columns = [
        "track_id",
        "track_name",
        "artists",
        "track_genre",
        "popularity",
        "energy",
        "valence"
    ]

    return records_to_json(
        result[columns]
    )


def distribution(df):
    result = df.copy()

    result["mood"] = result.apply(
        lambda row: mood_label(
            row["energy"],
            row["valence"]
        ),
        axis=1
    )

    return records_to_json(
        result.groupby("mood")
        .size()
        .reset_index(name="songs")
    )