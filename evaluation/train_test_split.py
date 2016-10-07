"""
split psl data truth file into train and test set and save into file with random state
"""
import pandas as pd
import numpy as np
import os
from sklearn.model_selection import KFold



DATA_PATH = "../psl/data/first_model/"



def main():
    data_split(cv_fold=10) 


def data_split(test_percent=0.1, cv_fold=5, seed=0):
    folder = "{0}/seed{1}/".format(DATA_PATH, seed)
    try:
        os.mkdir(folder)
        os.mkdir(folder + "test/")
        os.mkdir(folder + "cross_val/")
    except OSError:
        print "Either folder already exists or some crazy errors happened in creating folder!"
    test_train_split(folder, seed=seed, test_percent=test_percent)
    cross_validation_split(cv_fold, folder, seed) 


def cross_validation_split(cv_fold, folder, seed):
    df = pd.read_csv(folder + "cross_val/sensitive_truth_train.txt", delimiter="\t", 
                     header=None, names=["cell", "drug", "sensitivity_probability"])
    kf = KFold(n_splits=cv_fold, shuffle=True, random_state=seed)
    cv_folder = folder + "cross_val/{0}fold/".format(cv_fold)
    try:
        os.mkdir(cv_folder)
    except OSError:
        print "Either folder already exists or some crazy errors happened in creating folder!"
    fold = 1
    for train_idx, val_idx in kf.split(df):
        df.iloc[train_idx].to_csv(cv_folder + "fold{0}_train_sensitivity_truth.txt".format(fold), 
                                  index=False, sep="\t", header=None)
        df.iloc[val_idx].to_csv(cv_folder + "fold{0}_val_sensitivity_truth.txt".format(fold),
                                index=False, sep="\t", header=None)
        fold +=1


def test_train_split(folder, seed=0, test_percent=0.1):
    df = pd.read_csv(DATA_PATH + "sensitive_truth.txt", delimiter="\t", header=None,
                     names=["cell", "drug", "sensitivity_probability"])
    np.random.seed(seed)
    random_idx = np.random.permutation(df.index)
    test_size = int(len(df) * test_percent)
    test_idx = random_idx[:test_size]
    train_idx = random_idx[test_size:]
    test_df = df.iloc[test_idx].copy()
    train_df = df.iloc[train_idx].copy() 
    
    assert len(random_idx) == len(test_idx) + len(train_idx)
    assert len(df) == len(test_df) + len(train_df)
    
    test_df.to_csv(folder + "test/sensitive_truth_test.txt", sep="\t", index=False, header=None)
    test_df[["cell", "drug"]].to_csv(folder + "test/sensitive_truth_test_target.txt",
                                     sep="\t", index=False, header=None)
    train_df.to_csv(folder + "cross_val/sensitive_truth_train.txt", 
                    sep="\t", index=False, header=None)    


if __name__=="__main__":
    main()
