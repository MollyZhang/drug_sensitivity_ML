"""
split psl data truth file into train and test set and then split train into n-fold cross validation
save all files into folder named by random state seed
"""
import pandas as pd
import numpy as np
import subprocess
import os
from sklearn.model_selection import KFold



DATA_PATH = "../psl/data/first_model/"



def main():
    data_split(cv_fold=5) 


def data_split(test_percent=0.1, cv_fold=5, seed=0):
    folder = "{0}/seed{1}/".format(DATA_PATH, seed)
    try:
        subprocess.call(["rm", "-rf", folder]) 
        os.mkdir(folder)
        os.mkdir(folder + "test/")
        os.mkdir(folder + "cross_val/")
        cv_folder = folder + "cross_val/{0}fold/".format(cv_fold)
        os.mkdir(cv_folder)
    except OSError:
        print "Some crazy errors happened in creating folder!"
    train_file = test_train_split(folder, seed=seed, test_percent=test_percent)
    
    df = pd.read_csv(train_file, delimiter="\t", header=None,
                     names=["cell", "drug", "sensitivity_probability"])
    for fold, train_df, val_df in cross_validation_split(df, cv_fold=cv_fold, seed=seed):
        train_df.to_csv(cv_folder + "fold{0}_train.txt".format(fold), index=False, sep="\t", header=None)
        val_df.to_csv(cv_folder + "fold{0}_val_truth.txt".format(fold),
                      index=False, sep="\t", header=None)
        val_df[["cell", "drug"]].to_csv(cv_folder + "fold{0}_val_target.txt".format(fold),
                                        index=False, sep="\t", header=None)


def cross_validation_split(df, cv_fold=5, seed=0):
    kf = KFold(n_splits=cv_fold, shuffle=True, random_state=seed)
    fold = 0 
    for train_idx, val_idx in kf.split(df):
        train_df = df.iloc[train_idx].copy()
        val_df = df.iloc[val_idx].copy()
        fold +=1
        yield fold, train_df, val_df


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
    
    train_file = folder + "cross_val/sensitive_truth_train.txt"
    test_file = folder + "test/sensitive_truth_test.txt"
    test_target_file = folder + "test/sensitive_truth_test_target.txt"
     
    train_df.to_csv(train_file, sep="\t", index=False, header=None)    
    test_df.to_csv(test_file, sep="\t", index=False, header=None)
    test_df[["cell", "drug"]].to_csv(test_target_file, sep="\t", index=False, header=None)
    
    return train_file


if __name__=="__main__":
    main()
