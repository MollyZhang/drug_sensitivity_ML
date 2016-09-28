"""this script generates converts raw data to data suitable as psl input """

import pandas as pd
import numpy as np


DATA_FOLDER = "data/first_model/"
DRUG_TARGET_RAW = "../data/combined_annotations_CCLEmapped.tab"


def main():
    drug()
    gene()




def drug():
    df = pd.read_csv(DRUG_TARGET_RAW, delimiter="\t", header=None)
    drug_set = set(df[1])
    with open("data/first_model/drug.txt", "w") as f:
        for i, drug in enumerate(drug_set):
            f.write("D{0}\t{1}\n".format(i, drug))
        f.close()


def gene():
    df = pd.read_csv(DRUG_TARGET_RAW, delimiter="\t", header=None)
    gene_set = set(df[0])
    with open("data/first_model/gene.txt", "w") as f:
        for i, gene in enumerate(gene_set):
            f.write("G{0}\t{1}\n".format(i, gene))
        f.close()

    
if __name__=="__main__":
    main()
