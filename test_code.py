"""test script using pytest"""
import pandas as pd
import numpy as np
import generate_data

def test_percentile_scaler():
    df = pd.DataFrame(map(float, range(10)), columns=list("A"))
    df_percentile = generate_data.percentile_scaler(df)
    for idx in df.index:
        assert df_percentile["A"][idx] == (idx + 1)/10.0
