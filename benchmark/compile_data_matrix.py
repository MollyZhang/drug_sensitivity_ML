import pandas as pd
import numpy as np


PSL_DATA_DIR = "../psl/data/union/min_max/"


def main():
    df, gene_set = get_cell_drug_pairs()
    df = filling_features(df, gene_set)
    df.to_csv("data_table_minmax.tsv", sep="\t", index=False)


def filling_features(df, gene_set):
    active_df = pd.read_csv(PSL_DATA_DIR + "active.txt", delimiter="\t", header=None)
    essential_df = pd.read_csv(PSL_DATA_DIR + "essential.txt", delimiter="\t", header=None)

    gene_drug_dict = get_gene_drug_dict()
    features = {}
    for gene in gene_set:
        features[gene] = {"targeted": [], "active": [], "essential": []}
    
    for index, row in df.iterrows():
        print index
        active_cell_df = active_df[active_df[0] == row.cell].copy()
        essential_cell_df = essential_df[essential_df[0] == row.cell].copy() 
        
        for gene in features.keys():
            if row.drug in gene_drug_dict[gene]:
                features[gene]["targeted"].append(1)
            else:
                features[gene]["targeted"].append(0)
        
            activity = active_cell_df[active_cell_df[1] == gene][2].values[0]
            essentiality = essential_cell_df[essential_cell_df[1] == gene][2].values[0]
            features[gene]["active"].append(activity)
            features[gene]["essential"].append(essentiality)

    for gene in sorted(features.keys()):
        for rule in ["targeted", "active", "essential"]:
            df[gene + "_" + rule] = features[gene][rule]
    
    return df


def get_cell_drug_pairs():
    """overlap of cell-drug pairs from three different sources"""
    gene_drug_dict = get_gene_drug_dict()
    active_set, active_gene_set = get_active_cell_drug_set(gene_drug_dict)
    essential_set, essential_gene_set = get_essential_cell_drug_set(gene_drug_dict)
    sensitive_set, sensitive_df = get_sensitive_cell_drug_set()
    overlap_gene_set = set(gene_drug_dict.keys()).intersection(essential_gene_set).intersection(active_gene_set)
    overlap_cell_drug_set = sensitive_set.intersection(active_set).intersection(essential_set)
    sensitive_df = sensitive_df[sensitive_df.cell_drug_pair.isin(overlap_cell_drug_set)]
    sensitive_df.index = range(len(sensitive_df.index))
    sensitive_df['cell'] = [x.split("D")[0] for x in sensitive_df.cell_drug_pair]
    sensitive_df['drug'] = ["D" + x.split("D")[1] for x in sensitive_df.cell_drug_pair]
    return sensitive_df, overlap_gene_set


def get_gene_drug_dict():
    drug_target_file = PSL_DATA_DIR + "drug_target.txt"
    drug_target_df = pd.read_csv(drug_target_file, delimiter="\t", header=None)
    drug_target_dict = {}
    for index, row in drug_target_df.iterrows():
        if row[1] in drug_target_dict.keys():
            drug_target_dict[row[1]].append(row[0])
        else:
            drug_target_dict[row[1]] = [row[0]]
    return drug_target_dict


def get_active_cell_drug_set(gene_drug_dict):
    active_df = pd.read_csv(PSL_DATA_DIR + "active.txt", delimiter="\t", header=None)
    active_cell_drug_pairs = []
    for index, row in active_df.iterrows():
        if row[1] in gene_drug_dict.keys():
            for drug in gene_drug_dict[row[1]]:
                active_cell_drug_pairs.append(row[0] + drug)
    return set(active_cell_drug_pairs), set(active_df[1])


def get_essential_cell_drug_set(gene_drug_dict):
    essential_df = pd.read_csv(PSL_DATA_DIR + "essential.txt", delimiter="\t", header=None)
    cell_drug_pairs = []
    for index, row in essential_df.iterrows():
        if row[1] in gene_drug_dict.keys():
            for drug in gene_drug_dict[row[1]]:
                cell_drug_pairs.append(row[0] + drug)
    return set(cell_drug_pairs), set(essential_df[1])
    

def get_sensitive_cell_drug_set():
    sensitive_df = pd.read_csv(PSL_DATA_DIR + "sensitive_truth.txt", delimiter="\t", header=None)
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
