""" this script generates converts raw data to data suitable as psl input,
    and all data are the ones that lie in the overlap of three data sets  """

import pandas as pd
import numpy as np
from scipy import stats
from pprint import pprint as pp

SOURCE_FILE = "benchmark/data_table_10gene.tsv"
PSL_DATA_DIR = "psl/data/overlap/"
WRITE_DIR = "psl/data/overlap/10gene/"


def main():
    drug_to_save, gene_to_save, cell_to_save = parse_psl_overlapping_data()
    gene_keys = gene(gene_to_save)
    cell_keys = cell(cell_to_save)
    drug_keys = drug(drug_to_save)
    drug_gene_keys = write_drug_target(drug_to_save, gene_to_save)
    generate_cell_drug_target(cell_keys, drug_keys)
    

def generate_cell_drug_target(cell_keys, drug_keys):
    print "generate sensitive_target.txt"
    f_target = open(WRITE_DIR + "sensitive_target.txt", "w")
    for cell in cell_keys.keys():
        for drug in drug_keys.keys():
            f_target.write("{0}\t{1}\n".format(cell, drug))
    f_target.close()
 

def parse_psl_overlapping_data():
    """parse from overlapping data matrix used for SVM bench mark"""

    print "generate sensitive_truth.txt"
    df = pd.read_csv(SOURCE_FILE, delimiter="\t")
    sensitive_df = df[["cell", "drug", "sensitivity_label"]].copy()
    sensitive_df.to_csv(WRITE_DIR + "sensitive_truth.txt", sep="\t", header=None, index=False)
    
    print "generate active.txt"
    active_columns = [c for c in df.columns if "active" in c]
    active_df = df[["cell"] +  active_columns].copy()
    active_df = active_df.drop_duplicates()
    gene_to_save = [c.split("_")[0] for c in active_df.columns]
    active_df.columns = gene_to_save
    psl_active_df = pd.melt(active_df, var_name="gene", value_name="activity", id_vars=["cell"])
    psl_active_df.to_csv(WRITE_DIR + "active.txt", sep="\t", header=None, index=False)

    print "generate essential.txt"
    essen_columns = [c for c in df.columns if "essential" in c]
    essential_df = df[["cell"] +  essen_columns].copy()
    essential_df = essential_df.drop_duplicates()
    essential_df.columns = gene_to_save 
    psl_essen_df = pd.melt(essential_df, var_name="gene", value_name="essentiality", id_vars=["cell"])
    psl_essen_df.to_csv(WRITE_DIR + "essential.txt", sep="\t", header=None, index=False)

    return set(df.drug), set(gene_to_save), set(df.cell)

def gene(gene_to_save):
    """ save overlap between all drug target genes, active genes and essential genes to gene predicate file"""
    print "generate gene.txt"
    gene_df = pd.read_csv(PSL_DATA_DIR + "gene.txt", delimiter="\t", header=None)
    overlap_gene_df = gene_df[gene_df[0].isin(gene_to_save)].copy()
    gene_keys = dict(zip(overlap_gene_df[0], overlap_gene_df[1]))
    overlap_gene_df.to_csv(WRITE_DIR + "gene.txt", sep="\t", header=None, index=False) 
    return gene_keys


def cell(cell_to_save):
    print "generate cell.txt"
    cell_df = pd.read_csv(PSL_DATA_DIR + "cell.txt", delimiter="\t", header=None)
    overlap_cell_df = cell_df[cell_df[0].isin(cell_to_save)].copy()
    overlap_cell_df.to_csv(WRITE_DIR + "cell.txt", sep="\t", header=None, index=False)
    cell_keys = dict(zip(overlap_cell_df[0], overlap_cell_df[1]))
    return cell_keys


def drug(drug_to_save):
    print "generate drug.txt"
    drug_df = pd.read_csv(PSL_DATA_DIR + "drug.txt", delimiter="\t", header=None)
    overlap_drug_df = drug_df[drug_df[0].isin(drug_to_save)].copy()
    overlap_drug_df.to_csv(WRITE_DIR + "drug.txt", sep="\t", header=None, index=False)
    drug_keys = dict(zip(overlap_drug_df[0], overlap_drug_df[1]))
    return drug_keys


def write_drug_target(drug_to_save, gene_to_save):
    print "generate drug_target.txt"
    df = pd.read_csv(PSL_DATA_DIR + "drug_target.txt", delimiter="\t", header=None)
    overlap_df = df[df[0].isin(drug_to_save) & df[1].isin(gene_to_save)].copy()
    overlap_df.to_csv(WRITE_DIR + "drug_target.txt", sep="\t", header=None, index=False)
    drug_gene_keys = dict(zip(overlap_df[0], overlap_df[1]))
    return drug_gene_keys

        


if __name__=="__main__":
    main()
