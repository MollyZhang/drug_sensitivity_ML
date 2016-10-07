"""test script using pytest"""
import pandas as pd
import numpy as np
import generate_data
from evaluation import train_test_split


def test_percentile_scaler():
    df = pd.DataFrame(map(float, range(10)), columns=list("A"))
    df_percentile = generate_data.percentile_scaler(df)
    for idx in df.index:
        assert df_percentile["A"][idx] == (idx + 1)/10.0
        assert type(df_percentile["A"][idx]) == np.float64

def test_cross_validation_split():
    df = pd.DataFrame(range(20), columns=["A"])
    tests = []
    trains = []
    for fold, train_df, test_df in train_test_split.cross_validation_split(df):
        assert set(list(train_df.A) + list(test_df.A)) == set(df.A)
        tests += list(test_df.A)
        trains += list(train_df.A)

    assert fold == 5 # check default 5 fold cv
    assert len(set(tests)) == len(tests)
    for i in set(trains):
        assert trains.count(i) == 4

 
