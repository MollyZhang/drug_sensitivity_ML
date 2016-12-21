package edu.ucsc

import java.text.DecimalFormat;
import org.apache.commons.lang3.builder.ToStringBuilder;

import edu.umd.cs.psl.application.inference.MPEInference;
import edu.umd.cs.psl.application.learning.weight.maxlikelihood.MaxLikelihoodMPE;
import edu.umd.cs.psl.config.*
import edu.umd.cs.psl.database.DataStore
import edu.umd.cs.psl.database.Database;
import edu.umd.cs.psl.database.DatabasePopulator;
import edu.umd.cs.psl.database.Partition;
import edu.umd.cs.psl.database.ReadOnlyDatabase;
import edu.umd.cs.psl.database.rdbms.RDBMSDataStore
import edu.umd.cs.psl.database.rdbms.driver.H2DatabaseDriver
import edu.umd.cs.psl.database.rdbms.driver.H2DatabaseDriver.Type
import edu.umd.cs.psl.groovy.PSLModel;
import edu.umd.cs.psl.groovy.PredicateConstraint;
import edu.umd.cs.psl.groovy.SetComparison;
import edu.umd.cs.psl.model.argument.ArgumentType;
import edu.umd.cs.psl.model.argument.GroundTerm;
import edu.umd.cs.psl.model.argument.UniqueID;
import edu.umd.cs.psl.model.argument.Variable;
import edu.umd.cs.psl.model.atom.GroundAtom;
import edu.umd.cs.psl.model.function.ExternalFunction;
import edu.umd.cs.psl.ui.functions.textsimilarity.*
import edu.umd.cs.psl.ui.loading.InserterUtils;
import edu.umd.cs.psl.util.database.Queries;
import edu.umd.cs.psl.evaluation.statistics.*;


for (i=1; i<= 6; i++) {
    println "fold ${i}"
    ////////////////////////// initial setup ////////////////////////
    ConfigManager cm = ConfigManager.getManager()
    ConfigBundle config = cm.getBundle("first-model")
    
    def defaultPath = System.getProperty("java.io.tmpdir")
    String dbpath = config.getString("dbpath", defaultPath + File.separator + "first-model")
    DataStore data = new RDBMSDataStore(new H2DatabaseDriver(Type.Disk, dbpath, true), config)
    PSLModel m = new PSLModel(this, data)
    
    ////////////////////////// predicate declaration ////////////////////////
    m.add predicate: "DrugTarget",   types: [ArgumentType.UniqueID, ArgumentType.UniqueID]
    m.add predicate: "Active",       types: [ArgumentType.UniqueID, ArgumentType.UniqueID]
    m.add predicate: "Sensitive",    types: [ArgumentType.UniqueID, ArgumentType.UniqueID]
    
    ///////////////////////////// rules ////////////////////////////////////
    m.add rule : ( DrugTarget(D, G) & Active(C, G) ) >> Sensitive(C, D),  weight : 100
    m.add rule : ~Sensitive(C, D),  weight : 100
    
    println ""
    println "Rules with initial weights:"
    println m;
    
    //////////////////////////// data setup ///////////////////////////
    // loads data
    def dir = this.args[0]
    def target_dir = "seed0" + java.io.File.separator + "cross_val_6fold" + java.io.File.separator;
    def evidencePartition = new Partition(0);
    
    insert = data.getInserter(DrugTarget, evidencePartition);
    InserterUtils.loadDelimitedDataTruth(insert, dir+"drug_gene_targets.txt");
    
    insert = data.getInserter(Active, evidencePartition);
    InserterUtils.loadDelimitedDataTruth(insert, dir+"cell_gene_activity.txt");
    
    // add target atoms
    def trainTargetPartition = new Partition(1);
    insert = data.getInserter(Sensitive, trainTargetPartition);
    InserterUtils.loadDelimitedData(insert, dir+"sensitive_target.txt");
    
    Database db1 = data.getDatabase(trainTargetPartition, [DrugTarget, Active] as Set, evidencePartition);
    
    //////////////////////////// run inference ///////////////////////////
    MPEInference inferenceApp = new MPEInference(m, db1, config);
    inferenceApp.mpeInference();
    inferenceApp.close();
    
    println "saving inference results to result/"
    DecimalFormat formatter = new DecimalFormat("#.#######");
    def data_type = this.args[0].tokenize("/")[-1]

    def result_file = new File("result/simulation/${data_type}/yes_prior_no_WL_100/fold${i}_result.txt");
    result_file.write ""
    for (GroundAtom atom : Queries.getAllAtoms(db1, Sensitive)) {
        for (int i=0; i<2; i++) {
            result_file << atom.arguments[i].toString() + "\t"
        }
        result_file << formatter.format(atom.getValue()) + "\n"}
    
    // close the Databases to flush writes
    db1.close();
}
