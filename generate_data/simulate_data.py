"""
simulate perfect data with linear relations as well random noise
"""

import numpy as np
import itertools
import random
import train_test_split


NUM_CELL = 100
NUM_GENE_DRUG = 10


def main():
    simulate(multiple_drug_target=False)
    simulate(multiple_drug_target=True)


def simulate(multiple_drug_target=False):
    if multiple_drug_target:
        psl_folder="../psl/data/simulation/{0}_multiple_target/"
        matrix_file = "../data/similuated_matrix_{0}_multiple_target.tsv"
    else:
        psl_folder="../psl/data/simulation/{0}_single_target/"
        matrix_file = "../data/similuated_matrix_{0}_single_target.tsv"
   
    PSL1 = psl_folder + "drug_gene_targets.txt"
    PSL2 = psl_folder + "cell_gene_activity.txt"
    PSL3 = psl_folder + "sensitive_truth.txt"
    PSL4 = psl_folder + "sensitive_target.txt"
    drug_target = write_drug_target(PSL1, multiple_drug_target)
    expression_level = write_gene_activity(PSL2)
    linear_sensitivity, random_sensitivity = write_sensitivity(PSL3, PSL4, expression_level, drug_target)
    train_test_split.data_split(psl_folder.format("linear"), cv_fold=6, seed=0)
    train_test_split.data_split(psl_folder.format("random"), cv_fold=6, seed=0)
    compile_data_matrix(matrix_file, drug_target, expression_level, linear_sensitivity, random_sensitivity)

def write_drug_target(PSL1, multiple_drug_target):
    drug_target = {}
    f_linear = open(PSL1.format("linear"), "w")
    f_random = open(PSL1.format("random"), "w")
    for drug_id in range(NUM_GENE_DRUG):
        drug_target[drug_id] = [drug_id]
        f_linear.write("D{0}\tG{1}\n".format(drug_id, drug_id))
        f_random.write("D{0}\tG{1}\n".format(drug_id, drug_id))
        extra_targets = int(random.expovariate(0.5))
        other_genes = range(NUM_GENE_DRUG)
        other_genes.remove(drug_id)
        if multiple_drug_target:
            for each_extra in range(extra_targets):
                pick_a_gene = random.choice(other_genes)
                drug_target[drug_id].append(pick_a_gene)
                f_linear.write("D{0}\tG{1}\n".format(drug_id, pick_a_gene))
                f_random.write("D{0}\tG{1}\n".format(drug_id, pick_a_gene))
                other_genes.remove(pick_a_gene)
    f_linear.close()
    f_random.close()
    print drug_target
    return drug_target 


def write_gene_activity(PSL2):
    expression_level = {}
    f_linear = open(PSL2.format("linear"), "w")
    f_random = open(PSL2.format("random"), "w")
    for gene_id in range(NUM_GENE_DRUG):
        activities = np.random.uniform(0, 1, NUM_CELL)
        for cell_id in range(NUM_CELL):
            expression_level[(cell_id, gene_id)] = activities[cell_id]
            f_linear.write("C{0}\tG{1}\t{2}\n".format(cell_id, gene_id, activities[cell_id]))
            f_random.write("C{0}\tG{1}\t{2}\n".format(cell_id, gene_id, activities[cell_id]))
    f_linear.close()
    f_random.close()
    return expression_level


def write_sensitivity(file_truth, file_target, expression_level, drug_target): 
    random_sensitivity = {}
    linear_sensitivity = {}
    f_truth_linear = open(file_truth.format("linear"), "w")
    f_truth_random = open(file_truth.format("random"), "w")
    f_target_linear = open(file_target.format("linear"), "w")
    f_target_random = open(file_target.format("random"), "w")
    for cell_id in range(NUM_CELL):
        for drug_id in range(NUM_GENE_DRUG):
            average_gene_level = np.mean([expression_level[(cell_id, gene_id)] 
                                          for gene_id in drug_target[drug_id]])
            random_point = random.random()
            linear_sensitivity[(cell_id, drug_id)] = average_gene_level 
            random_sensitivity[(cell_id, drug_id)] = random_point
            f_truth_linear.write("C{0}\tD{1}\t{2}\n".format(cell_id, drug_id, average_gene_level))
            f_truth_random.write("C{0}\tD{1}\t{2}\n".format(cell_id, drug_id, random_point))
            f_target_linear.write("C{0}\tD{1}\n".format(cell_id, drug_id))
            f_target_random.write("C{0}\tD{1}\n".format(cell_id, drug_id))
    f_truth_linear.close()
    f_truth_random.close()
    f_target_linear.close()
    f_target_random.close()
    return linear_sensitivity, random_sensitivity


def compile_data_matrix(matrix_file, drug_target, expression_level, linear_sensitivity, random_sensitivity):
    """ rows label: cell-drug sensitivity
        features, gene1-10 activity in cell, gene1-10 whether targeted by drug """
    
    labels = {"linear": linear_sensitivity, "random": random_sensitivity}
    
    for data_type, sensitivity in labels.iteritems():
        f = open(matrix_file.format(data_type), "w")
        columns = ["cell-drug-pair", "cell", "drug"]
        for gene in ["G" + str(i) for i in range(NUM_GENE_DRUG)]:
            columns += [gene + "_targeted", gene + "_activity"]
        columns.append("sensitivity")
        f.write("\t".join(columns) + "\n")

        cell_drug_pairs = [i for i in itertools.product(range(NUM_CELL), range(NUM_GENE_DRUG))]
        for cell_id, drug_id in cell_drug_pairs:
            row = ["C" + str(cell_id) + "D" + str(drug_id), "C" + str(cell_id), "D" + str(drug_id)]
            for gene_id in range(NUM_GENE_DRUG):
                targeted = int(gene_id in drug_target[drug_id])
                activity = expression_level[(cell_id, gene_id)]
                row += [targeted, activity] 
            row.append(sensitivity[(cell_id, drug_id)])
            f.write("\t".join([str(i) for i in row]) + "\n")
        f.close()


if __name__ == "__main__":
    main()
