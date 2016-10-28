import pandas as pd
import numpy as np


PSL_DATA_DIR = "../psl/data/first_model/"


def main():
    df = get_cell_drug_pairs()




def get_cell_drug_pairs():
    """overlap of cell-drug pairs from three different sources"""
     
    gene_drug_dict = get_gene_drug_dict()
    active_set = get_active_cell_drug_set(gene_drug_dict)
    essential_set = get_essential_cell_drug_set(gene_drug_dict)
    sensitive_set, sensitive_df = get_sensitive_cell_drug_set()
    overlap_cell_drug_set = sensitive_set.intersection(active_set).intersection(essential_set)
    sensitive_df = sensitive_df[sensitive_df.cell_drug_pair.isin(overlap_cell_drug_set)]
    sensitive_df.index=sensitive_df.cell_drug_pair
    sensitive_df.drop("cell_drug_pair", 1, inplace=True)
    return sensitive_df

def get_gene_drug_dict():
    drug_target_file = "../psl/data/first_model/drug_target.txt"
    drug_target_df = pd.read_csv(drug_target_file, delimiter="\t", header=None)
    drug_target_dict = {}
    for index, row in drug_target_df.iterrows():
        if row[1] in drug_target_dict.keys():
            drug_target_dict[row[1]].append(row[0])
        else:
            drug_target_dict[row[1]] = [row[0]]
    return drug_target_dict


def get_active_cell_drug_set(gene_drug_dict):
    active_df = pd.read_csv("../psl/data/first_model/active.txt", delimiter="\t", header=None)
    active_cell_drug_pairs = []
    for index, row in active_df.iterrows():
        if row[1] in gene_drug_dict.keys():
            for drug in gene_drug_dict[row[1]]:
                active_cell_drug_pairs.append(row[0] + drug)
    return set(active_cell_drug_pairs)


def get_essential_cell_drug_set(gene_drug_dict):
    essential_df = pd.read_csv("../psl/data/first_model/essential.txt", delimiter="\t", header=None)
    cell_drug_pairs = []
    for index, row in essential_df.iterrows():
        if row[1] in gene_drug_dict.keys():
            for drug in gene_drug_dict[row[1]]:
                cell_drug_pairs.append(row[0] + drug)
    return set(cell_drug_pairs)
    

def get_sensitive_cell_drug_set():
    sensitive_df = pd.read_csv("../psl/data/first_model/sensitive_truth.txt", delimiter="\t", header=None)
    cell_drug_pairs = []
    for index, row in sensitive_df.iterrows():
        cell_drug_pairs.append(row[0] + row[1])
    sensitive_df.drop(0, 1, inplace=True)
    sensitive_df.drop(1, 1, inplace=True)
    sensitive_df["cell_drug_pair"] = cell_drug_pairs
    sensitive_df.rename(columns={2: "sensitivity_label"}, inplace=True)
    return set(cell_drug_pairs), sensitive_df






if __name__=="__main__":
    main()
