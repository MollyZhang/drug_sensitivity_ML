"""this script generates converts raw data to data suitable as psl input """

import pandas as pd
import numpy as np


DRUG_TARGET_RAW = "../data/combined_annotations_CCLEmapped.tab"
ESSEN_RAW = "../data/Achilles_QC_v2.4.3.rnai.Gs.gct"
MRNA_RAW = "../data/CCLE_Expression_Entrez_2012-09-29.gct"
DRUG_RESPON_RAW = "../data/CCLE_NP24.2009_Drug_data_2015.02.24.csv"


def main():
    #drug()
    #gene()
    cell()


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


def cell():
    # intersection of cell lines from all data sources
    df1 = pd.read_csv(ESSEN_RAW, delimiter="\t")
    cell1 = set(df1.columns)
    cell1.remove("Name")
    cell1.remove("Description")
    
    df2 = pd.read_csv(MRNA_RAW, low_memory=False, delimiter="\t")
    cell2 = set(df2.columns)
    cell2.remove("Name")
    cell2.remove("Description")

    df3 = pd.read_csv(DRUG_RESPON_RAW)
    cell3 = set(df3["CCLE Cell Line Name"])

    cell_set = cell1.intersection(cell2).intersection(cell3)
    with open("data/first_model/cell.txt", "w") as f:
        for i, cell in enumerate(cell_set):
            f.write("C{0}\t{1}\n".format(i, cell))
        f.close()

    
if __name__=="__main__":
    main()
