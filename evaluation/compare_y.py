import sklearn.metrics
import pandas as pd
import numpy as np
import scipy as sp


def main():
    train_file = "../psl/data/first_model/seed0/cross_val/5fold/fold1_train.txt"
    test_file = "../psl/data/first_model/seed0/cross_val/5fold/fold1_val.txt"
    infer_file = "../psl/result/first_model_cross_val_fold1_result.txt"

    tr_df = load_data(train_file)
    val_df = load_data(test_file)
    infer_df = load_data(infer_file)
    print calculate_accuracy(tr_df, infer_df)
    print calculate_accuracy(val_df, infer_df)


def load_data(file_name):
    rows = []
    with open(file_name, "r") as f:
        for line in f:
            items = line.strip("\n").split("\t")
            cell_drug_pair = items[0] + items[1]
            value = float(items[-1])
            rows.append({"cell_drug_pair": cell_drug_pair, "y": value})
    f.close()
    df = pd.DataFrame(rows)
    return df


def calculate_accuracy(truth_df, infer_df):
    infer_df = infer_df.loc[infer_df.cell_drug_pair.isin(truth_df.cell_drug_pair)].copy()
    df = pd.merge(truth_df, infer_df, on="cell_drug_pair", suffixes=["_truth", "_infer"]) 
    mse = sklearn.metrics.mean_squared_error(df.y_truth, df.y_infer)
    rho = sp.stats.spearmanr(df.y_truth, df.y_infer)[0]
    accuracy, auc = binary_result(df)
    return mse, rho, accuracy, auc






def binary_result(df):
    """ take >75% as label 1 and <25% as label 0, return accuracy"""

    df.loc[df.y_truth >= 0.75, "y_"] = 1 
    df.loc[df.y_truth <= 0.25, "y_"] = 0 
    binary_df = df.dropna().copy()
    binary_df.loc[binary_df.y_infer >= 0.5, "y"] = 1 
    binary_df.loc[binary_df.y_infer < 0.5, "y"] = 0
    accuracy = sklearn.metrics.accuracy_score(binary_df.y_, binary_df.y)
    auc = sklearn.metrics.roc_auc_score(binary_df.y_, binary_df.y)
    return accuracy, auc 


if __name__=="__main__":
    main()
