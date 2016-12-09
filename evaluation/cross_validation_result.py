import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib as mpl
mpl.rcParams['backend'] = "TkAgg"
from matplotlib import pyplot as plt

import compare_y

TRUTH = "../psl/data/overlap/10gene/seed0/cross_val_6fold/"
INFER_FOLDER = "../psl/result/one_gene/10gene/"


def main():
    pass

def cross_val_result(truth_folder, infer_folder):
    mse_rows = []
    rho_rows = []
    for fold in range(1, 7):
        infer_file = "{0}fold{1}_result.txt".format(infer_folder, fold)
        truth_train_file = "{0}fold{1}_train_truth.txt".format(truth_folder, fold)
        truth_val_file = "{0}fold{1}_val_truth.txt".format(truth_folder, fold)
        infer_df = compare_y.load_data(infer_file)
        truth_train_df = compare_y.load_data(truth_train_file)
        truth_val_df = compare_y.load_data(truth_val_file)
        train_mse, train_rho, _, _ = compare_y.calculate_accuracy(truth_train_df, infer_df)
        val_mse, val_rho, _, _ = compare_y.calculate_accuracy(truth_val_df, infer_df)
        mse_rows.append(val_mse)
        rho_rows.append(val_rho)
    return mse_rows, rho_rows
 

def comparing_wrong_and_correct_model():
    final_rows = []
    for data_scope in ["union", "overlap"]:  
        for model in ["wrong", "correct"]:
            rows = []
            for fold in range(1, 7):
                mse_dict = {}
                infer_file = INFER_FOLDER + "{0}_{1}_fold{2}_result.txt".format(data_scope, model, fold)
                truth_train_file = TRUTH.format(data_scope) + "fold{0}_train_truth.txt".format(fold)
                truth_val_file = TRUTH.format(data_scope) + "fold{0}_val_truth.txt".format(fold)
                infer_df = compare_y.load_data(infer_file)
                truth_train_df = compare_y.load_data(truth_train_file)
                truth_val_df = compare_y.load_data(truth_val_file)
                train_mse, train_rho, _, _ = compare_y.calculate_accuracy(truth_train_df, infer_df)
                val_mse, val_rho, _, _ = compare_y.calculate_accuracy(truth_val_df, infer_df)
                rows.append({"train_mse": train_mse, "val_mse": val_mse}) 
                rows.append({"train_rho": train_rho, "val_rho": val_rho}) 
            df = pd.DataFrame(rows)
            print data_scope, model
            print df.std() 
            final_rows.append({"mse": float(df.mean()["train_mse"]), 
                               "spearman rank correlation": float(df.mean()["train_rho"]),
                               "data_scope": data_scope, "model": model, "type": "train"})
            final_rows.append({"mse": float(df.mean()["val_mse"]), 
                               "spearman rank correlation": float(df.mean()["val_rho"]),
                               "data_scope": data_scope, "model": model, "type": "val"})
    df_final = pd.DataFrame(final_rows)
    print df_final
    g = sns.factorplot(x="model", y = "spearman rank correlation", col="data_scope", hue="type", data=df_final, 
                       kind="bar", size=4)
    g.set_xlabels("")
    plt.show()


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
