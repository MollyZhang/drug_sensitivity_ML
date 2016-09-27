import sklearn.metrics
import pandas as pd

TRUTH_FILE = "../data/ToyDrugExample/sensitive_truth.txt"
INFER_RESULT = "../result/toy_inference_result.txt"


def main():
    results = load_data(TRUTH_FILE, INFER_RESULT)
    print results
    truth = list(results.loc["truth"])
    inference = list(results.loc["inference"])
    print "mean squared error", sklearn.metrics.mean_squared_error(truth, inference)


def load_data(truth_file, inference_file):
    results = []
    for each_file in [truth_file, inference_file]:
        result = {}
        with open(each_file, "r") as f:
            for line in f:
                items = line.strip("\n").split("\t")
                cell_drug_pair = items[0] + items[1]
                value = float(items[-1])
                result[cell_drug_pair] = value
        results.append(result)
    df = pd.DataFrame(results)
    df = df.rename(index={0: "truth", 1: "inference"})
    return df

if __name__=="__main__":
    main()
