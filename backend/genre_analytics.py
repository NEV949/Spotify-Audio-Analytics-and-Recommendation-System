from utils import AUDIO_FEATURES, records_to_json

def genre_list(df):
    return sorted(df["track_genre"].dropna().unique().tolist())

def genre_detail(df, genre):
    result = df[
        df["track_genre"].fillna("").str.lower() == genre.lower()
    ]

    if result.empty:
        return None

    return {
        "genre": genre,
        "songs": int(len(result)),
        "average_popularity": round(float(result["popularity"].mean()), 2),
        "average_features": {
            feature: round(float(result[feature].mean()), 4)
            for feature in AUDIO_FEATURES
        }
    }

def statistics(df):
    result = (
        df.groupby("track_genre")
        .agg(
            songs=("track_id", "count"),
            average_popularity=("popularity", "mean"),
            average_energy=("energy", "mean"),
            average_danceability=("danceability", "mean"),
            average_valence=("valence", "mean"),
            average_acousticness=("acousticness", "mean"),
            average_tempo=("tempo", "mean")
        )
        .reset_index()
    )
    return records_to_json(result)
