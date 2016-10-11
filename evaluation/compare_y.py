import sklearn.metrics
import pandas as pd
import numpy as np



def main():
    train_file = "../psl/data/first_model/seed0/cross_val/5fold/fold1_train.txt"
    test_file = "../psl/data/first_model/seed0/cross_val/5fold/fold1_val.txt"
    infer_file = "../psl/result/first_model_cross_val_fold1_result.txt"

    tr_df, val_df, infer_df = load_data(train_file, test_file, infer_file)
    print calculate_accuracy(tr_df, infer_df)
    print calculate_accuracy(val_df, infer_df)



def load_data(train_file, test_file, infer_file):
    dataframes = []
    for each_file in [train_file, test_file, infer_file]:
        rows = []
        with open(each_file, "r") as f:
            for line in f:
                items = line.strip("\n").split("\t")
                cell_drug_pair = items[0] + items[1]
                value = float(items[-1])
                rows.append({"cell_drug_pair": cell_drug_pair, "sensitivity": value})
        f.close()
        df = pd.DataFrame(rows)
        dataframes.append(df)
    return dataframes


def calculate_accuracy(truth_df, infer_df):
    infer_df = infer_df.loc[infer_df.cell_drug_pair.isin(truth_df.cell_drug_pair)].copy()
    df = pd.merge(infer_df, truth_df, on="cell_drug_pair", suffixes=["_truth", "_infer"]) 
    truth = np.array(df["sensitivity_truth"])
    infer = np.array(df["sensitivity_infer"])
    mse = sklearn.metrics.mean_squared_error(truth, infer)
    return mse 


if __name__=="__main__":
    main()
