"""
initialize rule weights as numbers between 0-1 and plot weight learning + accuracy curve
"""

import numpy as np
import subprocess
import time
import os
import pandas as pd
import pprint

from evaluation import weight_learning_curve as wlc 


def main():
    sim = simulation("data/simulation/linear/", "result/simulation/linear")



def Simulation(data_folder, result):
    def __init__(self, data, result):
        self.data = data
        self.result = result

    def run():
        pass
 



def RandomInitialWeight(object):

    def __init__(self):
        self.initial_weights = self.initialize_weights() 
        self.weight_folder = "./result/random_initial_weight/weights_"
        
    def run_psl():
        subprocess.call(["mvn", "compile"])
        subprocess.call(["mvn", "dependency:build-classpath", "-Dmdep.outputFile=classpath.out"])
        for weights in self.initial_weights:
            print "weights: ", weights
            folder = self.weight_folder + "_".join(weights)
            try:
                os.mkdir(folder)  
            except:
                pass

            essen_w, active_w, prior_w = weights
            classpath = subprocess.check_output(["cat", "classpath.out"])
            log = subprocess.check_output(["java", "-cp", "./target/classes:{0}".format(classpath),
                         "edu.ucsc.ArgWeightLearning", essen_w, active_w, prior_w])
            df = wlc.parse_weight(log)
            df.to_csv(folder + "/weight_change.csv", sep="\t", index=None, header=None)
            for index, row in df.iterrows():
                print "iteration", index
                filename = "{0}/{1}.txt".format(folder, index)
                subprocess.call(["java", "-cp", "./target/classes:{0}".format(classpath), 
                                "edu.ucsc.ArgWeightInference", 
                                str(row.essential_rule), str(row.active_rule), 
                                str(row.sensitive_prior), filename])

    def initialize_weights(self):
        w = [] 
        w.append(["6"]*3)
        weight_range = range(1, 17, 3)
        for a in weight_range:
            for b in weight_range:
                c = 18-a-b
                if c > 0:
                    w.append([str(a),str(b),str(c)])
        return w

    def plot_result():
        for weights in self.initial_weights:
            folder = self.weight_folder + "_".join(weights)
            df = pd.read_csv(folder + "/weight_change.csv", header=None, delimiter="\t", 
                             names=["essential_rule", "active_rule", "sensitive_prior"])
            train_mse, test_mse = wlc.get_accuracy_curve(folder, len(df)-1)
            df['train_mse'] = train_mse
            df['test_mse'] = test_mse
            wlc.plotting(df, title="initial weights: "+"_".join(weights), 
                         save_to="../plots/random_initial_weight/weights_{0}.png".format("_".join(weights)))


if __name__=="__main__":
    main()
