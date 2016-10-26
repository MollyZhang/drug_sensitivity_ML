"""parse weight updates from PSL debug log and plot the rule weight change over iterations
"""
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import compare_y

TRAIN_FILE = "../psl/data/first_model/seed0/cross_val/5fold/fold1_train.txt"
TEST_FILE = "../psl/data/first_model/seed0/cross_val/5fold/fold1_val.txt"



def main():
    df = parse_weight("../psl/result/log/first_model_cross_val_fold1_log_stepsize5.txt")
    df['mse'] = get_accuracy_curve("../psl/result/log/weight_curve2")
    plotting(df)


def get_accuracy_curve(folder, iteration):
    train_df = compare_y.load_data(TRAIN_FILE)
    test_df = compare_y.load_data(TEST_FILE)
    train_accu = []
    test_accu = []
    for i in range(iteration + 1):
        infer_df = compare_y.load_data("{0}/{1}.txt".format(folder, i)) 
        train_mse, _, _ = compare_y.calculate_accuracy(train_df, infer_df)
        test_mse, _, _ = compare_y.calculate_accuracy(test_df, infer_df)
        train_accu.append(train_mse)
        test_accu.append(test_mse)
    return train_accu, test_accu


def parse_weight(log_file):
    rule_text = {"} ( DRUGTARGET(D, G) & ESSENTIAL(C, G) ) >> SENSITIVE(C, D)": "essential_rule",
                 "} ( DRUGTARGET(D, G) & ACTIVE(C, G) ) >> SENSITIVE(C, D)": "active_rule",
                 "} ~( SENSITIVE(C, D) )": "sensitive_prior"}
    weights = {"active_rule": [], "essential_rule": [], "sensitive_prior": []}
    
    if len(log_file) < 500:
        f = open(log_file, "r")
        all_lines = f.readlines()
        f.close()
    else:
        all_lines = log_file.split("\n")    

    for rule_text, rule in rule_text.iteritems():
        weights[rule] = [float(line.split(rule_text)[0].split("{")[-1])
                         for line in all_lines
                         if (rule_text in line)]
        weights[rule].pop(0) 
    df = pd.DataFrame(weights)
    return df


def plotting(df, title="", save_to=False):
    f, axarr = plt.subplots(nrows=2, ncols=1, sharex = True, squeeze=True)
    axarr[0].plot(df.index, df.essential_rule, "g", label="essential rule")
    axarr[0].plot(df.index, df.active_rule, "r", label="active rule")
    axarr[0].plot(df.index, df.sensitive_prior, "b", label="sensitive prior")
    axarr[0].set_ylabel("Rule weights")
    axarr[0].legend(loc="best")
    axarr[0].set_title(title)
    axarr[1].plot(df.index, df.train_mse, "c", label="train mse")
    axarr[1].plot(df.index, df.test_mse, "m", label = "test mse")
    axarr[1].set_ylabel("MSE")
    axarr[1].legend(loc="best")
    plt.xlabel("number of iterations")
    if save_to:
        plt.savefig(save_to, dpi=200, bbox_inches="tight")
    else:
        plt.show()


if __name__ == "__main__":
    main()
