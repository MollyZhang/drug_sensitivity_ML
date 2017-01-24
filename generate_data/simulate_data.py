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


def simulate(data_type="linear", multiple_drug_target=False):
    psl_folder="../psl/data/simulation/{0}/".format(data_type)
    matrix_file = "../data/similuated_matrix_{0}.tsv".format(data_type)
    PSL1 = psl_folder + "drug_gene_targets.txt"
    PSL2 = psl_folder + "cell_gene_activity.txt"
    PSL3 = psl_folder + "sensitive_truth.txt"
    PSL4 = psl_folder + "sensitive_target.txt"
    
    drug_target = write_drug_target(PSL1, multiple_drug_target)
    expression_level = write_gene_activity(PSL2)
    linear_sensitivity, random_sensitivity = write_sensitivity(PSL3, PSL4, data_type, expression_level, drug_target)
    compile_data_matrix(matrix_file, drug_target, data_type, expression_level, linear_sensitivity, random_sensitivity)
    train_test_split.data_split(psl_folder, cv_fold=6, seed=0)

def write_drug_target(filename, multiple_drug_target):
    drug_target = {}
    f = open(filename, "w")
    if multiple_drug_target:
        pass
    else:
        for drug_id in range(NUM_GENE_DRUG):
            for gene_id in range(NUM_GENE_DRUG):
                if drug_id == gene_id:
                    drug_target[drug_id] = [gene_id]
                    f.write("D{0}\tG{1}\t{2}\n".format(drug_id, gene_id, 1))
                else:
                    f.write("D{0}\tG{1}\t{2}\n".format(drug_id, gene_id, 0))
    f.close()
    return drug_target 


def write_gene_activity(filename):
    expression_level = {}
    with open(filename, "w") as f:
        for gene_id in range(NUM_GENE_DRUG):
            activities = np.random.uniform(0, 1, NUM_CELL)
            for cell_id in range(NUM_CELL):
                expression_level[(cell_id, gene_id)] = activities[cell_id]
                f.write("C{0}\tG{1}\t{2}\n".format(cell_id, gene_id, activities[cell_id]))
    f.close()
    return expression_level


def write_sensitivity(filename1, filename2, data_type, expression_level, drug_target): 
    random_sensitivity = {}
    linear_sensitivity = {}
    f_truth = open(filename1, "w")
    f_target = open(filename2, "w")
    for cell_id in range(NUM_CELL):
        for drug_id in range(NUM_GENE_DRUG):
            average_gene_level = np.mean([expression_level[(cell_id, gene_id)] 
                                          for gene_id in drug_target[drug_id]])
            random_point = np.random.uniform(0,1,1)[0]
            linear_sensitivity[(cell_id, drug_id)] = average_gene_level 
            random_sensitivity[(cell_id, drug_id)] = random_point
            if data_type == "linear":
                f_truth.write("C{0}\tD{1}\t{2}\n".format(cell_id, drug_id, average_gene_level))
            elif data_type == "random":
                f_truth.write("C{0}\tD{1}\t{2}\n".format(cell_id, drug_id, random_point))
            else:
                raise Exception("bad time")
            f_target.write("C{0}\tD{1}\n".format(cell_id, drug_id))
    f_truth.close()
    f_target.close()    
    return linear_sensitivity, random_sensitivity


def compile_data_matrix(matrix_file, drug_target, data_type, expression_level, linear_sensitivity, random_sensitivity):
    """ rows label: cell-drug sensitivity
        features, gene1-10 activity in cell, gene1-10 whether targeted by drug """

    # write header/column name
    f = open(matrix_file, "w")
    columns = ["cell-drug-pair", "cell", "drug"]
    for gene in ["G" + str(i) for i in range(NUM_GENE_DRUG)]:
        columns += [gene + "_targeted", gene + "_activity"]
    columns.append("sensitivity")
    f.write("\t".join(columns) + "\n")

    cell_drug_pairs = [i for i in itertools.product(range(NUM_CELL), range(NUM_GENE_DRUG))]
    for cell_id, drug_id in cell_drug_pairs:
        row = ["C" + str(cell_id) + "D" + str(drug_id), "C" + str(cell_id), "D" + str(drug_id)]
        linear_label = 0
        for gene_id in range(NUM_GENE_DRUG):
            targeted = int(gene_id in drug_target[drug_id])
            activity = expression_level[(cell_id, gene_id)]
            row += [targeted, activity] 
        if data_type == "linear":
            row.append(linear_sensitivity[(cell_id, drug_id)])
        elif data_type == "random":
            row.append(random_sensitivity[(cell_id, drug_id)])
        else:
            raise Exception("bad time")
        f.write("\t".join([str(i) for i in row]) + "\n")
    f.close()


if __name__ == "__main__":
    main()
