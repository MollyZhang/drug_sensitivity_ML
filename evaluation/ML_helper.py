import pandas as pd
from sklearn import model_selection, metrics
import scipy
import numpy as np

def load_data(file_name):
    df = pd.read_csv(file_name, sep="\t")
    label = df["sensitivity"].copy()
    data = df.drop("sensitivity", axis=1)
    data.set_index(data["cell-drug-pair"], inplace=True)
    data.drop("cell-drug-pair", axis=1, inplace=True)
    data.drop("cell", axis=1, inplace=True)
    data.drop("drug", axis=1, inplace=True)
    return data.as_matrix(), label.as_matrix()


def run_cross_val(X, Y, classifiers, n_fold=5, random_state=0):
    kf = model_selection.KFold(n_splits=n_fold, shuffle=True, random_state=random_state)
    mse_result_df = pd.DataFrame()
    spearman_result_df = pd.DataFrame()
    fold_num = 0
    for train, test in kf.split(Y):
        fold_num += 1
        tr, val = model_selection.train_test_split(train, test_size=0.2, random_state=random_state)
        x_train = X[tr]
        y_train = Y[tr]
        x_val = X[val]
        y_val = Y[val]
        x_test = X[test]
        y_test = Y[test]
    
        for classifier_name, clf in classifiers.iteritems():
            clf.fit(x_train, y_train)
            prediction = clf.predict(x_val)
            mse = metrics.mean_squared_error(prediction, y_val)
            rho = scipy.stats.spearmanr(prediction, y_val)
            mse_result_df.loc[fold_num, classifier_name] = mse
            spearman_result_df.loc[fold_num, classifier_name] = rho[0]
    return mse_result_df, spearman_result_df 
