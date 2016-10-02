"""this script generates converts raw data to data suitable as psl input """

import pandas as pd
import numpy as np
from scipy import stats
from pprint import pprint as pp

DRUG_TARGET_RAW = "../data/combined_annotations_CCLEmapped.tab"
ESSEN_RAW = "../data/Achilles_QC_v2.4.3.rnai.Gs.gct"
ESSEN_PERCENT = "../data/Achilles_QC_v2.4.3.rnai.Gs.percent.txt"
MRNA_RAW = "../data/CCLE_Expression_Entrez_2012-09-29.gct"
DRUG_RESPON_RAW = "../data/CCLE_NP24.2009_Drug_data_2015.02.24.csv"


def main():
    #drug_keys = drug()
    gene_keys = gene()
    cell_keys = cell()
    #target(drug_keys, gene_keys)
    essential(cell_keys, gene_keys)
    #active(cell_keys, gene_keys)


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
    """ save all drug target genes (~100 of them) to gene predicate file"""
    # TODO instead of drug targets, expand to all ~20,000 genes 
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
    cell_keys = {}
    with open("data/first_model/cell.txt", "w") as f:
        for i, cell in enumerate(cell_set):
            key = "C" + str(i)
            cell_keys[cell] = key
            f.write("{0}\t{1}\n".format(key, cell))
        f.close()
    return cell_keys


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


def essential(cell_keys, gene_keys):
    """generate essential.txt file for psl"""
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
        df = percentile_scaler(df)
        df.to_csv(ESSEN_PERCENT, sep="\t")

    f = open("data/first_model/essential.txt", "w")
    for cell in df.columns:
        for gene in gene_keys.keys():
            if gene in df.index:
                f.write("{0}\t{1}\t{2}\n".format(cell_keys[cell], gene_keys[gene], df[cell][gene]))
    f.close()


def active(cell_keys, gene_keys):
    df = pd.read_csv(MRNA_RAW, delimiter="\t")
    df.dropna(inplace=True)
    #print df.head()
    #df = average_duplicate_solutions(df)
    print df[df.Description=="TTL"]
    print len(df.Description)
    print len(set(df.Description))
    for gene in df.Description:
        if list(df.Description).count(gene)>1:
            print gene 

 
def remove_duplicate_solutions(df):
    """for gene essentiality and mRNA with multiple solutions
       remove all other solution rows except for first solution"""
    def pick_best_ATARI_solution(names):
        for name in names:
            if name.split("_")[1] == "1":
                return name

    genes = list(df.Description)
    dup_genes = set([gene for gene in genes if genes.count(gene)>1])
    for dup_gene in dup_genes:
        dup_rows = df[df.Description==dup_gene].copy()
        names_to_delete = list(dup_rows.Name)
        name_to_save = pick_best_ATARI_solution(names_to_delete)
        names_to_delete.remove(name_to_save)
        for each_name in names_to_delete: 
            df = df[df.Name != each_name]
    return df


def percentile_scaler(df):
    """ scale gene data to percentile within a cell
    """
    #TODO: expriment with scaling to percentile over all and percentile over one gene
    def take_negative(n):
        return -n
    df_percentile = df.copy()
    df = df.applymap(take_negative)
    for index, cell in enumerate(df.columns):
        print index, len(df.columns)
        for gene in df.index:
            pt = stats.percentileofscore(df[cell], df[cell][gene])
            df_percentile[cell][gene] =  pt/100
    return df_percentile 


if __name__=="__main__":
    main()
