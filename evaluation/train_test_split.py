"""
split psl data truth file into train and test set and save into file with random state
"""
import pandas as pd
import numpy as np
import os


DATA_PATH = "../psl/data/first_model/"



def main():
    test_train_split(seed=0, test_percent=0.1) 


def test_train_split(seed=0, test_percent=0.1):
    np.random.seed(seed)
    df = pd.read_csv(DATA_PATH + "sensitive_truth.txt", delimiter="\t",
                     header=None, names=["cell", "drug", "sensitivity_probability"])
    random_idx = np.random.permutation(df.index)
    test_size = int(len(df) * test_percent)
    test_idx = random_idx[:test_size]
    train_idx = random_idx[test_size:]
    assert len(random_idx) == len(test_idx) + len(train_idx)
    test_df = df.iloc[test_idx].copy()
    train_df = df.iloc[train_idx].copy() 
    assert len(df) == len(test_df) + len(train_df)
    
    folder = DATA_PATH + "seed" + str(seed) + "/"
    try:
        os.mkdir(folder)
        os.mkdir(folder + "test/")
        os.mkdir(folder + "cross_val/")
    except OSError:
        pass
    
    test_df.to_csv(folder + "test/sensitive_truth_test.txt", sep="\t", index=False, header=None)
    test_df[["cell", "drug"]].to_csv(folder + "test/sensitive_truth_test_target.txt",
                                     sep="\t", index=False, header=None)
    train_df.to_csv(folder + "cross_val/sensitive_truth_train.txt", 
                    sep="\t", index=False, header=None)


if __name__=="__main__":
    main()
