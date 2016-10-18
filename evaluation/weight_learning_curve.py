"""parse weight updates from PSL debug log and plot the rule weight change over iterations
"""
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import compare_y

TRUTH_FILE = "../psl/data/first_model/seed0/cross_val/5fold/fold1_train.txt"


def main():
    df = parse_weight("../psl/result/log/first_model_cross_val_fold1_log_stepsize5.txt")
    df['mse'] = get_accuracy_curve("../psl/result/log/weight_curve2")
    plotting(df)


def get_accuracy_curve(folder):
    truth_df = compare_y.load_data(TRUTH_FILE)
    accu = []
    for i in range(101):
        infer_df = compare_y.load_data("{0}/{1}.txt".format(folder, i)) 
        mse, _, _ = compare_y.calculate_accuracy(truth_df, infer_df)
        accu.append(mse)
    return accu


def parse_weight(log_file):
    rule_text = {"} ( DRUGTARGET(D, G) & ESSENTIAL(C, G) ) >> SENSITIVE(C, D)": "essential_rule",
                 "} ( DRUGTARGET(D, G) & ACTIVE(C, G) ) >> SENSITIVE(C, D)": "active_rule",
                 "} ~( SENSITIVE(C, D) )": "sensitive_prior"}
    weights = {"active_rule": [], "essential_rule": [], "sensitive_prior": []}
    
    f = open(log_file, "r")
    all_lines = f.readlines()
    f.close()
    
    for rule_text, rule in rule_text.iteritems():
        weights[rule] = [float(line.split(rule_text)[0].split("{")[-1])
                         for line in all_lines
                         if (rule_text in line and "kernel" in line)]
        weights[rule].pop(0) 
    df = pd.DataFrame(weights)
    df.to_csv(log_file + ".parsed_weights", 
              index=False, header=None, sep="\t") 
    return df


def plotting(df):
    df.plot(subplots=True, figsize=(8, 8));
    plt.xlabel("number of iterations") 
    plt.show()


if __name__ == "__main__":
    main()
