from utils import AUDIO_FEATURES

def matrix(df):
    features = AUDIO_FEATURES + ["popularity"]
    corr = df[features].corr()

    return {
        "features": features,
        "matrix": [
            [
                round(float(corr.loc[row, column]), 4)
                for column in features
            ]
            for row in features
        ]
    }
