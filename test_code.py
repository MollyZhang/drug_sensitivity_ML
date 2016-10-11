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
    
    df1 = pd.DataFrame(np.random.normal(size=1000))
    df1_percentile = generate_data.percentile_scaler(df1)
    df1_p = df1_percentile[0]
    df1_p[df1_p >= 0.75] = 1
    df1_p[df1_p <= 0.25] = 0
    bottom25 = df1_p.value_counts().iloc[0]
    top25 = df1_p.value_counts().iloc[1]    
    assert bottom25 in [top25-1, top25, top25+1]
    



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

 
