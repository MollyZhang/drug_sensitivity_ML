"""this script generates converts raw data to data suitable as psl input """

import pandas as pd
import numpy as np
from pprint import pprint as pp

DRUG_TARGET_RAW = "../data/combined_annotations_CCLEmapped.tab"
ESSEN_RAW = "../data/Achilles_QC_v2.4.3.rnai.Gs.gct"
MRNA_RAW = "../data/CCLE_Expression_Entrez_2012-09-29.gct"
DRUG_RESPON_RAW = "../data/CCLE_NP24.2009_Drug_data_2015.02.24.csv"


def main():
    #drug_keys = drug()
    #gene_keys = gene()
    #cell()
    #target(drug_keys, gene_keys)
    essential()
    #active()

def drug():
    df = pd.read_csv(DRUG_TARGET_RAW, delimiter="\t", header=None)
    drug_set = set(df[1])
    drug_keys = {}
    with open("data/first_model/drug.txt", "w") as f:
        for i, drug in enumerate(drug_set):
            key = "D" + str(i)
            drug_keys[drug] = key
            f.write("{0}\t{1}\n".format(key, drug))
        f.close()
    return drug_keys


def gene():
    df = pd.read_csv(DRUG_TARGET_RAW, delimiter="\t", header=None)
    gene_set = set(df[0])
    gene_keys = {}
    with open("data/first_model/gene.txt", "w") as f:
        for i, gene in enumerate(gene_set):
            key = "G" + str(i)
            gene_keys[gene] = key
            f.write("G{0}\t{1}\n".format(key, gene))
        f.close()
    return gene_keys


def cell():
    # union of cell lines from all data sources
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

    cell_set = cell1.union(cell2).union(cell3)
    with open("data/first_model/cell.txt", "w") as f:
        for i, cell in enumerate(cell_set):
            f.write("C{0}\t{1}\n".format(i, cell))
        f.close()


def target(drug_keys, gene_keys):
    df = pd.read_csv(DRUG_TARGET_RAW, delimiter="\t", header=None)
    target = {}
    for drug, gene in zip(df[1], df[0]):
        if drug in target.keys():
            target[drug].append(gene)
        else:
            target[drug] = [gene]
    f = open("data/first_model/target.txt", "w")
    for drug, genes in target.iteritems():
        for gene in genes:
            f.write("{0}\t{1}\n".format(drug_keys[drug], gene_keys[gene]))
    f.close()


def essential():
    df = pd.read_csv(ESSEN_RAW, delimiter="\t") 
    df.dropna(inplace=True)
    df = average_duplicate_solutions(df)
    genes = list(df.Description)
    print len(genes)
    print len(set(genes))


def average_duplicate_solutions(df):
    genes = list(df.Description)
    dup_genes = set([gene for gene in genes if genes.count(gene)>1])
    for dup_gene in dup_genes:
        dup_rows_mean = df[df.Description==dup_gene].copy().mean()
        dup_rows_mean["Name"] = dup_gene + "_mean"
        dup_rows_mean["Description"] = dup_gene
        df = df[df.Description != dup_gene]
        df = df.append(dup_rows_mean, ignore_index=True)
    return df


def active():
    pass

    
if __name__=="__main__":
    main()
