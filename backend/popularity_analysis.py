from utils import AUDIO_FEATURES, records_to_json

def statistics(df):
    return {
        "min": int(df["popularity"].min()),
        "max": int(df["popularity"].max()),
        "mean": round(float(df["popularity"].mean()), 2),
        "median": round(float(df["popularity"].median()), 2)
    }

def relationships(df):
    corr = df[["popularity"] + AUDIO_FEATURES].corr()["popularity"]

    result = [
        {
            "feature": feature,
            "correlation": round(float(corr[feature]), 4)
        }
        for feature in AUDIO_FEATURES
    ]

    return sorted(
        result,
        key=lambda x: abs(x["correlation"]),
        reverse=True
    )

def vs_feature(df, feature):
    if feature not in AUDIO_FEATURES:
        raise ValueError(f"Unsupported feature: {feature}")

    result = df[["popularity", feature]].dropna()

    if len(result) > 3000:
        result = result.sample(3000, random_state=42)

    return records_to_json(result)
