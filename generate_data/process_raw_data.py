""" this script generates converts raw data to data suitable as psl input """

import pandas as pd
import numpy as np
import subprocess
import os
from scipy import stats
from pprint import pprint as pp
from sklearn import preprocessing
import train_test_split



FOLDER = "../psl/data/master_data_{0}/"

DRUG_TARGET = "../raw_data/combined_annotations_CCLEmapped.tab"
ACHILLES = "../raw_data/Achilles_QC_v2.4.3.rnai.Gs.{0}.gct"
MRNA = "../raw_data/CCLE_Expression_Entrez_2012-09-29.{0}.gct"
SENSITIVE = "../raw_data/CCLE_NP24.2009_Drug_data_2015.02.24.ActArea.{0}.csv"


def main():
    #convert_all_data(scaling="percent")    
    collect_overlapping_subset(subsets=["active", "essential"], scaling="percent")


def collect_overlapping_subset(subsets=[], scaling=""):
    # collect
    input_folder = FOLDER.format(scaling) 
    label_df = pd.read_csv(input_folder + "sensitive_truth.txt", delimiter="\t", header=None)
    drug_target_df = pd.read_csv(input_folder + "drug_target.txt", delimiter="\t", header=None)
    cells = set(label_df[0])
    genes = set(drug_target_df[1])
    dfs = {}
    for subset in subsets:
        dfs[subset] = pd.read_csv(input_folder + "{0}.txt".format(subset), delimiter="\t", header=None)
        cells = cells.intersection(set(dfs[subset][0]))
        genes = genes.intersection(set(dfs[subset][1]))
    drugs = set(drug_target_df[drug_target_df[1].isin(genes)][0])
   
    # filter and save
    output_folder = input_folder + "_".join(subsets) + "_overlap/"
    try: 
        subprocess.call(["rm", "-rf", output_folder])
        os.mkdir(output_folder)
    except OSError:
        raise Exception("bad time")
 
    label_df = label_df[label_df[0].isin(cells)]
    label_df = label_df[label_df[1].isin(drugs)]
    label_df.to_csv(output_folder + "sensitive_truth.txt", sep="\t", index=None, header=None)
    label_df[[0,1]].to_csv(output_folder + "sensitive_target.txt", sep="\t", index=None, header=None)
    
    drug_target_df = drug_target_df[drug_target_df[0].isin(drugs)]
    drug_target_df = drug_target_df[drug_target_df[1].isin(genes)]
    drug_target_df.to_csv(output_folder + "drug_target.txt", sep="\t", index=None, header=None)
 
    for predicate_name, predicate_set in zip(["cell", "drug", "gene"], [cells, drugs, genes]):
        predicate_df = pd.read_csv(input_folder + "{0}.txt".format(predicate_name), 
                                   delimiter="\t", header=None)
        predicate_df = predicate_df[predicate_df[0].isin(predicate_set)]
        predicate_df.to_csv(output_folder + "{0}.txt".format(predicate_name), 
                            sep="\t", index=None, header=None)

    for subset_name, subset_df in dfs.iteritems():
        subset_df = subset_df[subset_df[0].isin(cells)]
        subset_df = subset_df[subset_df[1].isin(genes)]
        subset_df.to_csv(output_folder + "{0}.txt".format(subset_name), 
                         sep="\t", index=None, header=None)
    train_test_split.data_split(output_folder, cv_fold=6, seed=0)



def convert_all_data(scaling="percent"):
    """
    from raw data create a master version of psl data with specified scaling
    """
    output = FOLDER.format(scaling)
    drugs, genes, _ = drug_target(output=output, scaling=scaling)
    cells = sensitive(drugs, output=output, scaling=scaling)
    cells = active_and_essential(cells, genes, predicate="active", output=output, scaling=scaling)
    cells = active_and_essential(cells, genes, predicate="essential", output=output, scaling=scaling)
    train_test_split.data_split(output, cv_fold=6, seed=0)


def sensitive(drugs, output="", scaling=""):
    cells = {}
    f_cell = open(output + "cell.txt", "w")
    f_truth = open(output + "sensitive_truth.txt", "w")
    f_target = open(output + "sensitive_target.txt", "w")
    df = pd.read_csv(SENSITIVE.format(scaling), delimiter="\t")
    for index, row in df.iterrows():   
        cell_name = row["CCLE Cell Line Name"]
        if cell_name not in cells.keys():
            cell_key = "C" + str(len(cells))
            cells[cell_name] = cell_key 
            f_cell.write("{0}\t{1}\n".format(cell_key, cell_name)) 
        drug_key = drugs[row.Compound]
        cell_key = cells[cell_name]
        f_truth.write("{0}\t{1}\t{2}\n".format(cell_key, drug_key, row.ActArea))
        f_target.write("{0}\t{1}\n".format(cell_key, drug_key))
    f_target.close()
    f_truth.close()
    f_cell.close()
    return cells


def tissue(cell_keys):
    print "generate tissue.txt and is_tissue.txt"
    tissues = []
    for name, key in cell_keys.iteritems():
        tissue = "_".join(name.split("_")[1:])
        if tissue == "": # some cell lines doesn't have a tissue name
            continue 
        elif tissue == "LUNG.1":
            tissue = tissue[:-2]
        tissues.append(tissue)
    tissues = sorted(list(set(tissues)))
    tissue_keys = {}
    with open(DATA_FOLDER + "tissue.txt", "w") as f:
        for i, tissue in enumerate(tissues):
            key = "T" + str(i)
            tissue_keys[tissue] = key
            f.write("{0}\t{1}\n".format(key, tissue))
        f.close()

    print "generate is_tissue.txt"
    f = open(DATA_FOLDER + "is_tissue.txt", "w")
    for name, key in cell_keys.iteritems():
        tissue = "_".join(name.split("_")[1:])
        if tissue == "": # some cell lines doesn't have a tissue name
            continue 
        elif tissue == "LUNG.1":
            tissue = tissue[:-2]
        f.write("{0}\t{1}\n".format(cell_keys[name], tissue_keys[tissue]))
    f.close()


def drug_target(output, scaling="", write=True):
    f_drug = open(output + "drug.txt", "w")
    f_gene = open(output + "gene.txt", "w")
    f_target = open(output + "drug_target.txt", "w")
    df = pd.read_csv(DRUG_TARGET, delimiter="\t", header=None)
    drugs = {}
    genes = {}
    drug_targets = {}
    for drug, gene in zip(df[1], df[0]):
        if drug not in drugs.keys():
            drug_key = "D" + str(len(drugs))
            drugs[drug] = drug_key
            if write: 
                f_drug.write("{0}\t{1}\n".format(drug_key, drug))
        if gene not in genes.keys():
            gene_key = "G" + str(len(genes))
            genes[gene] = gene_key 
            if write:
                f_gene.write("{0}\t{1}\n".format(gene_key, gene))
        
        drug_key, gene_key = drugs[drug], genes[gene]
        if drug_key not in drug_targets.keys():
            drug_targets[drug_key] = [gene_key]
            if write:
                f_target.write("{0}\t{1}\n".format(drug_key, gene_key))
        elif gene_key not in drug_targets[drug_key]:
            drug_targets[drug_key].append(gene_key)
            if write:
                f_target.write("{0}\t{1}\n".format(drug_key, gene_key))
    return drugs, genes, drug_targets


def active_and_essential(cells, genes, predicate="", output="", scaling=""):
    if predicate=="essential":
        df = pd.read_csv(ACHILLES.format(scaling), delimiter="\t", index_col="Description")
        cell_names = df.columns 
    elif predicate=="active":
        df = pd.read_csv(MRNA.format(scaling), delimiter="\t", index_col="Description")
        cell_names = df.columns[1:]
    else:
        raise Exception("not supported")    

    f_out = open(output + "{0}.txt".format(predicate), "w")
    f_cell = open(output + "cell.txt", "a")
    for cell_name in cell_names:
        if cell_name not in cells.keys():
            cell_key = "C" + str(len(cells))
            cells[cell_name] = cell_key 
            f_cell.write("{0}\t{1}\n".format(cell_key, cell_name)) 
        for gene_name in genes.keys():
            if gene_name in df.index:
                f_out.write("{0}\t{1}\t{2}\n".format(cells[cell_name], genes[gene_name],
                                                       df[cell_name][gene_name]))
    f_out.close()
    f_cell.close()
    return cells


if __name__=="__main__":
    main()
