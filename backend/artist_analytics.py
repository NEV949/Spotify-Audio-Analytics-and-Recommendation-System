import ast
import pandas as pd

from utils import AUDIO_FEATURES, records_to_json


def split_artists(value):
    """
    Convert the artists field into individual artist names.

    Examples:
        Drake
        Drake;Future
        Drake;Future;The Weeknd
        ['Drake', 'Future']
    """

    if pd.isna(value):
        return []

    value = str(value).strip()

    if not value:
        return []

    # Spotify dataset uses semicolon-separated artists
    if ";" in value:
        return [
            artist.strip()
            for artist in value.split(";")
            if artist.strip()
        ]

    # Handle Python-list format if present
    if value.startswith("[") and value.endswith("]"):
        try:
            artists = ast.literal_eval(value)

            if isinstance(artists, list):
                return [
                    str(artist).strip()
                    for artist in artists
                    if str(artist).strip()
                ]

        except (ValueError, SyntaxError):
            pass

    # Fallback for comma-separated artists
    if "," in value:
        return [
            artist.strip()
            for artist in value.split(",")
            if artist.strip()
        ]

    # Single artist
    return [value]


def create_artist_rows(df):
    """
    Split songs containing multiple artists into
    separate logical artist rows.
    """

    result = df.copy()

    result["artist_list"] = result["artists"].apply(
        split_artists
    )

    result = result.explode("artist_list")

    result["artist"] = (
        result["artist_list"]
        .astype(str)
        .str.strip()
    )

    result = result[
        result["artist"].notna()
        & (result["artist"] != "")
    ]

    return result


def search_artists(df, query="", limit=50):
    """
    Search individual artists.

    Multiple artists in one song are counted separately.
    """

    result = create_artist_rows(df)

    artists = (
        result.groupby("artist")
        .size()
        .reset_index(name="songs")
        .sort_values(
            "songs",
            ascending=False
        )
    )

    if query:
        q = query.strip().lower()

        artists = artists[
            artists["artist"]
            .str.lower()
            .str.contains(
                q,
                regex=False,
                na=False
            )
        ]

    return records_to_json(
        artists.head(limit)
    )


def artist_detail(df, artist):
    """
    Return analytics for one individual artist.
    """

    result = create_artist_rows(df)

    artist_clean = artist.strip().lower()

    # Exact artist match
    result = result[
        result["artist"]
        .str.lower()
        == artist_clean
    ].copy()

    if result.empty:
        return None

    # Avoid duplicate dataset records
    result = result.drop_duplicates(
        subset=["track_id"]
    )

    songs = (
        result[
            [
                "track_id",
                "track_name",
                "album_name",
                "track_genre",
                "popularity"
            ]
        ]
        .sort_values(
            "popularity",
            ascending=False
        )
        .head(20)
    )

    average_features = {}

    for feature in AUDIO_FEATURES:
        if feature in result.columns:
            average_features[feature] = round(
                float(result[feature].mean()),
                4
            )

    return {
        "artist": artist,
        "songs": int(len(result)),
        "average_popularity": round(
            float(result["popularity"].mean()),
            2
        ),
        "average_features": average_features,
        "top_songs": records_to_json(songs)
    }