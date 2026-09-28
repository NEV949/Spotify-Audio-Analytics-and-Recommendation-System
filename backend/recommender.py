import numpy as np
from utils import AUDIO_FEATURES, records_to_json


def recommend(df, track_id, limit=10):
    # --------------------------------------------------
    # 1. Find the selected song
    # --------------------------------------------------
    seed_rows = df[df["track_id"] == track_id]

    if seed_rows.empty:
        return None

    seed = seed_rows.iloc[0]
    seed_cluster = int(seed["cluster"])

    # --------------------------------------------------
    # 2. Prepare candidate songs
    # --------------------------------------------------
    candidates = df[
        df["track_id"] != track_id
    ].copy()

    if candidates.empty:
        return {
            "seed": records_to_json(seed_rows.head(1))[0],
            "cluster": seed_cluster,
            "recommendations": []
        }

    # Remove duplicate occurrences of the same song
    # under different genres.
    candidates = candidates.drop_duplicates(
        subset=["track_name", "artists"]
    ).copy()

    # --------------------------------------------------
    # 3. Convert audio features to numeric values
    # --------------------------------------------------
    feature_cols = AUDIO_FEATURES

    seed_features = (
        seed[feature_cols]
        .astype(float)
        .to_numpy()
    )

    candidate_features = (
        candidates[feature_cols]
        .astype(float)
        .to_numpy()
    )

    # --------------------------------------------------
    # 4. Standardize each audio feature
    # --------------------------------------------------
    mean = candidate_features.mean(axis=0)
    std = candidate_features.std(axis=0)

    # Avoid division by zero
    std[std == 0] = 1

    seed_scaled = (seed_features - mean) / std
    candidates_scaled = (
        candidate_features - mean
    ) / std

    # --------------------------------------------------
    # 5. Normalize vectors for cosine similarity
    # --------------------------------------------------
    seed_norm = np.linalg.norm(seed_scaled)

    candidate_norms = np.linalg.norm(
        candidates_scaled,
        axis=1,
        keepdims=True
    )

    seed_scaled = (
        seed_scaled /
        max(seed_norm, 1e-12)
    )

    candidates_scaled = (
        candidates_scaled /
        np.maximum(candidate_norms, 1e-12)
    )

    # --------------------------------------------------
    # 6. Audio similarity
    # --------------------------------------------------
    audio_similarity = (
        candidates_scaled @ seed_scaled
    )

    candidates["audio_similarity"] = audio_similarity

    # --------------------------------------------------
    # 7. Cluster similarity
    # --------------------------------------------------
    candidates["cluster_similarity"] = (
        candidates["cluster"] == seed_cluster
    ).astype(float)
    
    # Same cluster = 1
    # Different cluster = 0

    # --------------------------------------------------
    # 8. Popularity similarity
    # --------------------------------------------------
    seed_popularity = float(seed["popularity"])

    candidates["popularity_similarity"] = (
        1 -
        (
            abs(
                candidates["popularity"].astype(float)
                - seed_popularity
            ) / 100
        )
    )

    # Keep values between 0 and 1
    candidates["popularity_similarity"] = (
        candidates["popularity_similarity"]
        .clip(0, 1)
    )

    # --------------------------------------------------
    # 9. Final hybrid recommendation score
    # --------------------------------------------------
    candidates["similarity"] = (
        0.75 * candidates["audio_similarity"]
        + 0.15 * candidates["cluster_similarity"]
        + 0.10 * candidates["popularity_similarity"]
    )

    # --------------------------------------------------
    # 10. Rank recommendations
    # --------------------------------------------------
    candidates = candidates.sort_values(
        "similarity",
        ascending=False
    )

    candidates = candidates.head(limit)

    # --------------------------------------------------
    # 11. Return response
    # --------------------------------------------------
    columns = [
        "track_id",
        "track_name",
        "artists",
        "album_name",
        "track_genre",
        "popularity",
        "cluster",
        "similarity"
    ]

    return {
        "seed": records_to_json(
            seed_rows.head(1)
        )[0],

        "cluster": seed_cluster,

        "recommendations": records_to_json(
            candidates[columns]
        )
    }