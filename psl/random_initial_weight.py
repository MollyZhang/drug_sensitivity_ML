"""
initialize rule weights as numbers between 0-1 and plot weight learning + accuracy curve
"""

import numpy as np
import subprocess
import time
import os
import pandas as pd


from evaluation import weight_learning_curve as wlc 






def main():
    plot_result()




def plot_result():
    initial_weights = initialize_weights()
    for weights in initial_weights:
        print weights
        folder = "./result/random_initial_weight/weights_" + "_".join(weights)
        df = pd.read_csv(folder + "/weight_change.csv", header=None, delimiter="\t", 
                         names=["essential_rule", "active_rule", "sensitive_prior"])
        df['mse'] = wlc.get_accuracy_curve(folder, 50)
        wlc.plotting(df, title=" ".join(weights), 
                     save_to="../plots/random_initial_weight/weights_{0}.png".format("_".join(weights)))


def run_experiment():
    subprocess.call(["mvn", "compile"])
    subprocess.call(["mvn", "dependency:build-classpath", "-Dmdep.outputFile=classpath.out"])

    initial_weights = initialize_weights()
    for weights in initial_weights:
       # 30 min per iteration
        print "weights: ", weights
        t1 = time.time()
        folder = "./result/random_initial_weight/weights_" + "_".join(weights)
        try:
            os.mkdir(folder)  
        except:
            pass

        essen_w, active_w, prior_w = weights
        classpath = subprocess.check_output(["cat", "classpath.out"])
        log = subprocess.check_output(["java", "-cp", "./target/classes:{0}".format(classpath),
                         "edu.ucsc.ArgWeight", essen_w, active_w, prior_w])
        df = wlc.parse_weight(log)
        df.to_csv(folder + "/weight_change.csv", sep="\t", index=None, header=None)
        for index, row in df.iterrows():
            print "iteration", index
            filename = "{0}/{1}.txt".format(folder, index)
            subprocess.call(["java", "-cp", "./target/classes:{0}".format(classpath), 
                             "edu.ucsc.AccuracyCurve", 
                             str(row.essential_rule), str(row.active_rule), 
                             str(row.sensitive_prior), filename])
        t2 = time.time()
        print "seconds it took to try one set of intial weights: ", t2-t1



def initialize_weights():
    w = [] 
    weight_range = map(lambda x: x/10.0, range(1, 10))
    for a in weight_range:
        for b in weight_range:
            for c in weight_range:
                if np.isclose(a+b+c, 1):
                    w.append([str(a),str(b),str(c)]) 
    return w


if __name__=="__main__":
    main()
