"""
initialize rule weights as numbers between 0-1 and plot weight learning + accuracy curve
"""

import numpy as np
import subprocess



def main():
    subprocess.call(["mvn", "compile"])
    subprocess.call(["mvn", "dependency:build-classpath", "-Dmdep.outputFile=classpath.out"])


    initial_weights = initialize_weights()
    for weights in initial_weights:
        classpath = subprocess.check_output(["cat", "classpath.out"])
        subprocess.call(["java", "-cp", "./target/classes:{0}".format(classpath),
                         "edu.ucsc.ToyDrugExample"])
        break




def initialize_weights():
    w = [] 
    weight_range = map(lambda x: x/10.0, range(1, 10))
    for a in weight_range:
        for b in weight_range:
            for c in weight_range:
                if np.isclose(a+b+c, 1):
                    w.append([a,b,c]) 
    return w


if __name__=="__main__":
    main()
