import math
import pandas as pd

AUDIO_FEATURES = [
    "danceability", "energy", "loudness", "acousticness",
    "valence", "tempo", "speechiness", "instrumentalness", "liveness"
]

def clean_value(value):
    if pd.isna(value):
        return None
    if hasattr(value, "item"):
        value = value.item()
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value

def records_to_json(df):
    return [
        {k: clean_value(v) for k, v in row.items()}
        for row in df.to_dict(orient="records")
    ]
