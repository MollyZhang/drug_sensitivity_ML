"""
split psl data truth file into train and test set and save into file with random state
"""
import pandas as pd
import numpy as np


DATA_PATH = "../psl/data/first_model/"
TEST_PERCENT = 0.1



def main():
    df = pd.read_csv(DATA_PATH + "sensitive_truth.txt", header=None, delimiter="\t")
    random_idx = np.random.permutation(df.index)
    test_size = int(len(df) * TEST_PERCENT)
    test_idx = random_idx[:test_size]
    train_idx = random_idx[test_size:]
    print len(test_idx)
    print len(train_idx)
    test_df = df.iloc[test_idx]
    




if __name__=="__main__":
    main()
