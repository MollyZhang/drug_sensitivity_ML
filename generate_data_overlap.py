""" this script generates converts raw data to data suitable as psl input,
    and all data are the ones that lie in the overlap of three data sets  """

import pandas as pd
import numpy as np
from scipy import stats
from pprint import pprint as pp


PSL_DATA_DIR = "psl/data/first_model/"
WRITE_DIR = "psl/data/overlap_cell_gene/"


def main():
    gene_keys = gene()
    cell_keys = cell()
    #drug_keys = drug()
    #drug_target(drug_keys, gene_keys)
    #essential(cell_keys, gene_keys)
    #not_essential(cell_keys, gene_keys)
    #active(cell_keys, gene_keys)
    #sensitive(cell_keys, drug_keys)
 

def gene():
    """ save overlap between all drug target genes, active genes and essential genes to gene predicate file"""
    print "generate gene.txt"
    drug_df = pd.read_csv(PSL_DATA_DIR + "drug_target.txt", delimiter="\t", header=None)
    active_df = pd.read_csv(PSL_DATA_DIR + "active.txt", delimiter="\t", header=None)
    essential_df = pd.read_csv(PSL_DATA_DIR + "essential.txt", delimiter="\t", header=None)
 
    overlap_gene_set = set(drug_df[1]).intersection(set(active_df[1])).intersection(set(essential_df[1]))
    gene_df = pd.read_csv(PSL_DATA_DIR + "gene.txt", delimiter="\t", header=None)
    overlap_gene_df = gene_df[gene_df[0].isin(overlap_gene_set)].copy()
    gene_keys = dict(zip(overlap_gene_df[0], overlap_gene_df[1]))
    overlap_gene_df.to_csv(WRITE_DIR + "gene.txt", sep="\t", header=None, index=False) 
    return gene_keys


def cell():
    # intersection of cell lines from all data
    print "generate cell.txt"
    drug_df = pd.read_csv(PSL_DATA_DIR + "sensitive_truth.txt", delimiter="\t", header=None)
    active_df = pd.read_csv(PSL_DATA_DIR + "active.txt", delimiter="\t", header=None)
    essential_df = pd.read_csv(PSL_DATA_DIR + "essential.txt", delimiter="\t", header=None)
    
    cell_set = set(active_df[0]).intersection(set(drug_df[0])).intersection(set(essential_df[0]))
    cell_df = pd.read_csv(PSL_DATA_DIR + "cell.txt", delimiter="\t", header=None)
    overlap_cell_df = cell_df[cell_df[0].isin(cell_set)].copy()
    overlap_cell_df.to_csv(WRITE_DIR + "cell.txt", sep="\t", header=None, index=False)
    cell_keys = dict(zip(overlap_cell_df[0], overlap_cell_df[1]))
    return cell_keys


def drug_target(drug_keys, gene_keys):
    print "generate drug_target.txt"
    df = pd.read_csv(DRUG_TARGET_RAW, delimiter="\t", header=None)
    drug_target = {}
    for drug, gene in zip(df[1], df[0]):
        if drug in drug_target.keys():
            drug_target[drug].append(gene)
        else:
            drug_target[drug] = [gene]
    f = open("psl/data/first_model/drug_target.txt", "w")
    for drug, genes in drug_target.iteritems():
        for gene in genes:
            f.write("{0}\t{1}\n".format(drug_keys[drug], gene_keys[gene]))
    f.close()


def essential(cell_keys, gene_keys):
    """generate essential.txt file for psl"""
    print "generate essential.txt"
    def take_negative(n):
        return -n
    try: 
        df = pd.read_csv(ESSEN_PERCENT, delimiter="\t", index_col="Description")
    except IOError: 
        # clean and build percentile file from scratch if it doesn't exist
        print "creating the percentile version of the essential file, takes ~20 min"
        df = pd.read_csv(ESSEN_RAW, delimiter="\t") 
        df.dropna(inplace=True)
        df = remove_duplicate_solutions(df)
        df = df.set_index("Description")
        df = df.drop("Name", axis=1)
        df = df.applymap(take_negative)
        df = percentile_scaler(df)
        df.to_csv(ESSEN_PERCENT, sep="\t")

    f = open("psl/data/first_model/essential.txt", "w")
    for cell in set(df.columns).intersection(set(cell_keys.keys())):
        for gene in gene_keys.keys():
            if gene in df.index:
                f.write("{0}\t{1}\t{2}\n".format(cell_keys[cell], gene_keys[gene], df[cell][gene]))
    f.close()


def not_essential(cell_keys, gene_keys):
    """generate not_essential.txt file for psl"""
    print "generate not_essential.txt"
    df = pd.read_csv(ESSEN_PERCENT, delimiter="\t", index_col="Description")
    f = open("psl/data/first_model/not_essential.txt", "w")
    for cell in set(df.columns).intersection(set(cell_keys.keys())):
        for gene in gene_keys.keys():
            if gene in df.index:
                f.write("{0}\t{1}\t{2}\n".format(cell_keys[cell], gene_keys[gene], 1-df[cell][gene]))
    f.close()


def active(cell_keys, gene_keys):
    # TODO currently gene "TTL" has two rows and both rows are dropped, could deal better    
    print "generate active.txt"
    try:
        df = pd.read_csv(MRNA_PERCENT, delimiter="\t", index_col="Description")
    except IOError:
        # clean and build percentile file from scratch if it doesn't exist
        print "creating the percentile version of the file, takes ~10 hours :("
        df = pd.read_csv(MRNA_RAW, low_memory=False, delimiter="\t")
        df.dropna(inplace=True)
        df = df[df.Description != "TTL"]
        df = df.set_index("Description")
        df = df.drop("Name", axis=1)
        df = percentile_scaler(df)
        df.to_csv(MRNA_PERCENT, sep="\t")
    
    f = open("psl/data/first_model/active.txt", "w")
    for cell in set(df.columns).intersection(set(cell_keys.keys())):
        for gene in gene_keys.keys():
            if gene in df.index:
                f.write("{0}\t{1}\t{2}\n".format(cell_keys[cell], gene_keys[gene], df[cell][gene]))
    f.close()

 
def sensitive(cell_keys, drug_keys):
    # sensitive truth value between cell line and drug pairs covered in CCLE data
    # as well as sensitive target which is a exhaustive list of all cell-drug pairs
    print "generate sensitive.txt"
    try:
        df = pd.read_csv(DRUG_RESPON_PERCENT, delimiter="\t")
    except IOError:
        print "creating the percentile version of the file, takes ~5 min"
        df = pd.read_csv(DRUG_RESPON_RAW)
        df = df[["CCLE Cell Line Name", "Compound", "ActArea"]].copy()
        df.ActArea = percentile_scaler(pd.DataFrame(df.ActArea))
        df.to_csv(DRUG_RESPON_PERCENT, sep="\t", index=False)

    cells = set(df["CCLE Cell Line Name"])
    drugs = set(df["Compound"])
    f_truth = open("psl/data/first_model/sensitive_truth.txt", "w")
    for cell in cells:
        for drug in drugs:
            ActArea = df[(df["CCLE Cell Line Name"] == cell) & (df["Compound"] == drug)].ActArea
            if len(ActArea) == 0:
                continue
            elif len(ActArea) > 1:
                raise Exception("bad times")
            else:
                f_truth.write("{0}\t{1}\t{2}\n".format(cell_keys[cell], 
                                                       drug_keys[drug], ActArea.values[0]))
    f_truth.close()

    f_target = open("psl/data/first_model/sensitive_target.txt", "w")
    for cell in cell_keys.values():
        for drug in drug_keys.values():
            f_target.write("{0}\t{1}\n".format(cell, drug))
    f_target.close()



if __name__=="__main__":
    main()
