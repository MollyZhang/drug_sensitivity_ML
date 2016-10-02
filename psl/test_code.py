"""test script using pytest"""
import pandas as pd
import numpy as np
import generate_data

def test_percentile_scaler():
    df = pd.DataFrame(np.random.randint(0, 10, size=(4,4)), 
                      columns=list("ABCD"))
    df_percentile = generate_data.percentile_scaler(df)
    for column in df.columns:
        for idx in df.index:
            assert df_percentile[column][idx] >= 0 and df_percentile[column][idx] <= 1
