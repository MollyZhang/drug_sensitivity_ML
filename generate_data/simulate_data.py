"""
simulate perfect data with linear relations as well random noise
"""

import numpy as np
import itertools
import train_test_split

NUM_CELL = 100
NUM_GENE_DRUG = 10


def main():
    simulate(data_type="linear")
    simulate(data_type="random")


def simulate(data_type="linear"):
    psl_folder="../psl/data/simulation/{0}/".format(data_type)
    matrix_file = "../data/similuated_matrix_{0}.tsv".format(data_type)
    PSL1 = psl_folder + "drug_gene_targets.txt"
    PSL2 = psl_folder + "cell_gene_activity.txt"
    PSL3 = psl_folder + "sensitive_truth.txt"
    PSL4 = psl_folder + "sensitive_target.txt"


    # write PSL drug targets
    with open(PSL1, "w") as f1:
        for drug_id in range(NUM_GENE_DRUG):
            for gene_id in range(NUM_GENE_DRUG):
                if drug_id == gene_id:
                    f1.write("D{0}\tG{1}\t{2}\n".format(drug_id, gene_id, 1))
                else:
                    f1.write("D{0}\tG{1}\t{2}\n".format(drug_id, gene_id, 0))
    f1.close()

    # write PSL data cell-gene activivity
    expression_level = {}
    with open(PSL2, "w") as f2:
        for gene_id in range(NUM_GENE_DRUG):
            activities = np.random.uniform(0, 1, NUM_CELL)
            for cell_id in range(NUM_CELL):
                expression_level[(cell_id, gene_id)] = activities[cell_id]
                f2.write("C{0}\tG{1}\t{2}\n".format(cell_id, gene_id, activities[cell_id]))
    f2.close()
    
    # write PSL data cell-drug sensitivity from linear calculation of cell-gene acitivity
    f3 = open(PSL3, "w")
    f4 = open(PSL4, "w")
    for cell_id in range(NUM_CELL):
        for drug_id in range(NUM_GENE_DRUG):
            if data_type == "linear":
                sensitivity = expression_level[(cell_id, drug_id)]
            elif data_type == "random":
                sensitivity = np.random.uniform(0,1,1)[0]
            f3.write("C{0}\tD{1}\t{2}\n".format(cell_id, drug_id, sensitivity))
            f4.write("C{0}\tD{1}\n".format(cell_id, drug_id))
    f3.close()
    f4.close()    

    # compile PSL data into data matrix for other ML methods
    # rows label: cell-drug sensitivity
    # features, gene1-10 activity in cell, gene1-10 whether targeted by drug
    f5 = open(matrix_file, "w")
    columns = ["cell-drug-pair", "cell", "drug"]
    for gene in ["G" + str(i) for i in range(NUM_GENE_DRUG)]:
        columns += [gene + "_targeted", gene + "_activity"]
    columns.append("sensitivity")
    f5.write("\t".join(columns) + "\n")

    cell_drug_pairs = [i for i in itertools.product(range(NUM_CELL), range(NUM_GENE_DRUG))]
    for cell_id, drug_id in cell_drug_pairs:
        row = ["C" + str(cell_id) + "D" + str(drug_id), "C" + str(cell_id), "D" + str(drug_id)]
        linear_label = 0
        for gene_id in range(NUM_GENE_DRUG):
            targeted = int(gene_id == drug_id)
            activity = expression_level[(cell_id, gene_id)]
            linear_label += targeted * activity
            row += [targeted, activity] 
        if data_type == "linear":
            row.append(linear_label)
        else:
            row.append(str(np.random.uniform(0,1,1)[0]))
        f5.write("\t".join([str(i) for i in row]) + "\n")
    f5.close()
    train_test_split.data_split(psl_folder, cv_fold=6, seed=0)


if __name__ == "__main__":
    main()
