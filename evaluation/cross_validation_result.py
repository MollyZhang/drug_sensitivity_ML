import pandas as pd
import numpy as np
from matplotlib import pyplot as plt

import compare_y

TRUTH_FOLDER = "../psl/data/overlap_cell_gene/seed0/cross_val_6fold/"
INFER_FOLDER = "../psl/result/overlap/"


def main():
    truth = TRUTH_FOLDER + "fold{0}_{1}_truth.txt"
    infer = INFER_FOLDER + "cross_val_fold{0}_{1}_result.txt"
    rows = []
    for fold in range(1, 7):
        mse_dict = {}
        for datatype in ["train", "val"]:
            truth_df = compare_y.load_data(truth.format(fold, datatype))
            infer_df = compare_y.load_data(infer.format(fold, datatype))
            mse, _, _ = compare_y.calculate_accuracy(truth_df, infer_df)
            mse_dict[datatype] = mse           
        rows.append(mse_dict)
    df = pd.DataFrame(rows)
    print df
    print df.mean()
    print df.std()
    #plotting(df)


def plotting(df):
    mean = df.mean()
    std = df.std()
    ax = mean.plot.bar(yerr=std, rot=30, alpha=0.75)
    ax.set_ylabel("Mean Squared Error")
    for rect in ax.patches:
        height = rect.get_height()
        height_label = "%.3f" % height
        ax.text(rect.get_x() + rect.get_width()/2, height + 0.01, height_label)
    plt.show()


def prettifying_df_for_bar_plot(df):
    nice_df = pd.DataFrame(index=["both_rules", "active_rule", "essential_rule"],
                           columns = ["train", "test"])
    for name in df.index:
        exp_type = name.split("_")[0]
        rest = "_".join(name.split("_")[1:])
        nice_df.loc[rest][exp_type] = df[name]
    return nice_df 
    




if __name__=="__main__":
    main()
