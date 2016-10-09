# drug_sensitivity_ML
This repository contains scripts pertaining to apply PSL (Probablistic Soft Logic) to cancer cell sensitivity to drugs using data from CCLE (Cancer Cell Line Encyclopedia).  
To read more about PSL: https://psl.umiacs.umd.edu  
To read more about CCLE: https://portals.broadinstitute.org/ccle/home  

### project structure (updated 10-9-2016)
    psl/    maven project and java/groovy/python codes for PSL applied to drug sensitity data
    intelliJ-psl/    use intelliJ IDE to run psl groovy project files
    profiling/  python or jupyter notebook script aiming at understanding/profiling of data
    evaluation/ python folder to calculate accuracies of psl result
    generate_data.py    python code to convert raw data into psl input format
    configure_intelliJ_for_psl.md   instruction to configure psl MAVEN project with groovy support in IntelliJ IDEA 
 
### List of data files (updated 10-06-2016)
    
    ----------------------------- RAW Data ------------------------------------------------------
    ## Downloaded from project Achilles https://portals.broadinstitute.org/achilles
    Achilles_QC_v2.4.3.rnai.Gs.gct
    Achilles_v2.4_SampleInfo_small.txt
    Achilles_v3.3.8.Gs.gct
    Achilles_v3.3.8_SampleInfo.txt
    
    ## Downloaded from CCLE https://portals.broadinstitute.org/ccle/home
    CCLE_Expression_Entrez_2012-09-29.gct
    CCLE_MUT_CNA_AMP_DEL_binary_Revealer.gct
    CCLE_NP24.2009_Drug_data_2015.02.24.csv
    CCLE_NP24.2009_profiling_2012.02.20.csv
    CCLE_Oncomap3_2012-04-09.maf
    CCLE_copynumber_byGene_2013-12-03.txt
    CCLE_hybrid_capture1650_hg19_NoCommonSNPs_NoNeutralVariants_CDS_2012.05.07.maf
    CCLE_sample_info_file_2012-10-18.txt 
    
    ## drug target data compiled by Verina and Kiley
    combined_annotations_CCLEmapped.tab
    
    ------------------------- generated data ----------------------------------------------------
    ## percentile of raw files (each value is converted to a percentile respective to its column)
    Achilles_QC_v2.4.3.rnai.Gs.percentgct
    CCLE_Expression_Entrez_2012-09-29.percentgct
    CCLE_NP24.2009_Drug_data_2015.02.24.ActAreaPercentcsv
