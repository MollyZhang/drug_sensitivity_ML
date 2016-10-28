import pandas as pd
import numpy as np


PSL_DATA_DIR = "../psl/data/first_model/"


def main():
    df = get_cell_drug_pairs()




def get_cell_drug_pairs():
    """overlap of cell-drug pairs from three different sources"""
    df = pd.read_csv(PSL_DATA_DIR + "sensitive_truth.txt", delimiter="\t", header=None)





    print df







if __name__=="__main__":
    main()
