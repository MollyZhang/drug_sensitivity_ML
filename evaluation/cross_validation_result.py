import pandas as pd
import numpy as np
from matplotlib import pyplot as plt


import compare_y



def main():
    train_file = "../psl/data/first_model/seed0/cross_val/5fold/fold{0}_train.txt"
    test_file = "../psl/data/first_model/seed0/cross_val/5fold/fold{0}_val.txt"
    infer_file = "../psl/result/first_model_cross_val_fold{0}_result.txt" 
    rows = []
    for fold in range(1, 6):
        tr_df, val_df, infer_df = compare_y.load_data(train_file.format(fold),
                                                      test_file.format(fold),
                                                      infer_file.format(fold))
        tr_mse, tr_accuracy, tr_auc = compare_y.calculate_accuracy(tr_df, infer_df)
        test_mse, test_accuracy, test_auc = compare_y.calculate_accuracy(val_df, infer_df)
        rows.append({"train_mse": tr_mse, "test_mse": test_mse})
                     #"train_accuracy": tr_accuracy, "test_accuracy": test_accuracy, 
                     #"train_auc_score": tr_auc, "test_auc_score": test_auc})
    df = pd.DataFrame(rows)
    plotting(df)


def plotting(df):
    mean = df.mean()
    std = df.std()
    print mean
    print std
    mean.plot.bar(yerr=std)
    plt.show()

if __name__=="__main__":
    main()
