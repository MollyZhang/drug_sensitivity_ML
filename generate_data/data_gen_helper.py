""" helper script for various stuff """

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
    """ scale gene data to percentile within a cell""" 
    # TODO: expriment with scaling to percentile over all and percentile over one gene 
    df_percentile = df.copy() 
    df = df.applymap(float) 
    for index, cell in enumerate(df.columns): 
        print "converting {0}th column of all {1} columns".format(index+1, len(df.columns)) 
        for gene in df.index: 
            pt = stats.percentileofscore(df[cell], df[cell][gene]) 
            df_percentile[cell][gene] =  pt/100 
    return df_percentile  
 
 
def minmax_scaler(df): 
    """ scale data to [0, 1] using min-max scaling""" 
    min_max_scaler = preprocessing.MinMaxScaler() 
    return pd.DataFrame(min_max_scaler.fit_transform(df),  
                        columns=df.columns, index=df.index)
