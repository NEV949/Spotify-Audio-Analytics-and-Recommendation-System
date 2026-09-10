"""PySpark pipeline: clean Spotify tracks, scale features, K-Means, write Hive-ready Parquet."""

from __future__ import annotations

import argparse

from pyspark.ml.clustering import KMeans
from pyspark.ml.feature import Normalizer, StandardScaler, VectorAssembler
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

AUDIO_FEATURES = [
    "danceability",
    "energy",
    "loudness",
    "acousticness",
    "valence",
    "tempo",
    "speechiness",
    "instrumentalness",
    "liveness",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="hdfs://namenode:9000/data/spotify/raw/tracks.csv")
    parser.add_argument("--clean-output", default="hdfs://namenode:9000/data/spotify/processed/tracks_clean")
    parser.add_argument("--output", default="hdfs://namenode:9000/data/spotify/processed/songs_clustered")
    parser.add_argument("--k", type=int, default=8)
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    spark = (
        SparkSession.builder.appName("spotify-kmeans-pipeline")
        .config("spark.sql.session.timeZone", "UTC")
        .getOrCreate()
    )

    raw = spark.read.option("header", True).option("inferSchema", True).csv(args.input)
    rename = {}
    if "track_genre" not in raw.columns and "genre" in raw.columns:
        rename["genre"] = "track_genre"
    if "id" in raw.columns and "track_id" not in raw.columns:
        rename["id"] = "track_id"
    if "name" in raw.columns and "track_name" not in raw.columns:
        rename["name"] = "track_name"
    df = raw
    for src, dst in rename.items():
        if src in df.columns:
            df = df.withColumnRenamed(src, dst)

    keep = [
        "track_id",
        "track_name",
        "artists",
        "album_name",
        "track_genre",
        "popularity",
        *AUDIO_FEATURES,
    ]
    present = [c for c in keep if c in df.columns]
    df = df.select(*present).dropDuplicates(["track_id"] if "track_id" in present else present)

    for col in ["popularity", *AUDIO_FEATURES]:
        if col in df.columns:
            df = df.withColumn(col, F.col(col).cast("double"))
    df = df.na.drop(subset=[c for c in AUDIO_FEATURES if c in df.columns])

    df.write.mode("overwrite").parquet(args.clean_output)

    assembler = VectorAssembler(inputCols=AUDIO_FEATURES, outputCol="features")
    assembled = assembler.transform(df)
    scaler = StandardScaler(
        inputCol="features",
        outputCol="scaled_features",
        withMean=True,
        withStd=True,
    )
    scaled = scaler.fit(assembled).transform(assembled)
    kmeans = KMeans(featuresCol="scaled_features", predictionCol="cluster", k=args.k, seed=args.seed)
    clustered = kmeans.fit(scaled).transform(scaled)
    normalizer = Normalizer(inputCol="scaled_features", outputCol="norm_features", p=2.0)
    clustered = normalizer.transform(clustered)

    hive_cols = present + ["cluster"]
    hive_ready = clustered.select(*[c for c in hive_cols if c in clustered.columns])
    hive_ready.write.mode("overwrite").parquet(args.output)

    spark.stop()


if __name__ == "__main__":
    main()
