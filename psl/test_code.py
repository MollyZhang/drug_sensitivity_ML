"""test script using pytest"""
import pandas as pd
import numpy as np
import generate_data

def test_scaler():
    df = pd.DataFrame(np.random.randint(0, 10, size=(4,4)), 
                      columns=list("ABCD"))
    print df
    assert True
