"""
split psl data truth file into train and test set and then split train into n-fold cross validation
save all files into folder named by random state seed
"""
import pandas as pd
import numpy as np
import subprocess
import os
from sklearn.model_selection import KFold, train_test_split



DATA_PATH = "../psl/data/simulation/"

def main():
    data_split(DATA_PATH + "linear/", cv_fold=6, seed=0)
    data_split(DATA_PATH + "random/", cv_fold=6, seed=0)


def data_split(path, cv_fold=6, seed=0):
    folder = "{0}/seed{1}/".format(path, seed)
    try:
        subprocess.call(["rm", "-rf", folder]) 
        os.mkdir(folder)
        cv_folder = folder + "cross_val_{0}fold/".format(cv_fold)
        os.mkdir(cv_folder)
    except OSError:
        print "Some crazy errors happened in creating folder!"

    #train_file = test_train_split(folder, seed=seed, test_percent=test_percent)
    
    df = pd.read_csv(path + "sensitive_truth.txt", delimiter="\t", header=None,
                     names=["cell", "drug", "sensitive_label"])

    for fold, tr_df, val_df, test_df in cross_validation_split(df, cv_fold=cv_fold, seed=seed):
        dfs = {"train": tr_df, "val": val_df, "test": test_df}
        for data_type, df in dfs.iteritems():
            df.to_csv(cv_folder + "fold{0}_{1}_truth.txt".format(fold, data_type), 
                      index=False, sep="\t", header=None)
            df[["cell", "drug"]].to_csv(cv_folder + "fold{0}_{1}_to_predict.txt".format(fold, data_type), 
                                        index=False, sep="\t", header=None)


def cross_validation_split(df, cv_fold=6, seed=0):
    kf = KFold(n_splits=cv_fold, shuffle=True, random_state=seed)
    fold = 0 
    for train_idx, test_idx in kf.split(df):
        tr_idx, val_idx = train_test_split(train_idx, test_size=1.0/(cv_fold-1), random_state=seed)
        train_df = df.iloc[tr_idx].copy()
        val_df = df.iloc[val_idx].copy()
        test_df = df.iloc[test_idx].copy()
        fold +=1
        yield fold, train_df, val_df, test_df


if __name__=="__main__":
    main()
