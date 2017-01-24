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

String result_path = "result/essential_overlap/rule_swapping_experiment/6/"
for (i=1; i<= 6; i++) {
    ////////////////////////// initial setup ////////////////////////
    ConfigManager cm = ConfigManager.getManager()
    ConfigBundle config = cm.getBundle("first-model")
    
    def defaultPath = System.getProperty("java.io.tmpdir")
    String dbpath = config.getString("dbpath", defaultPath + File.separator + "first-model")
    DataStore data = new RDBMSDataStore(new H2DatabaseDriver(Type.Disk, dbpath, true), config)
    PSLModel m = new PSLModel(this, data)
    
    ////////////////////////// predicate declaration ////////////////////////
    m.add predicate: "DrugTarget",   types: [ArgumentType.UniqueID, ArgumentType.UniqueID]
    m.add predicate: "Essential",    types: [ArgumentType.UniqueID, ArgumentType.UniqueID]
    m.add predicate: "Sensitive",    types: [ArgumentType.UniqueID, ArgumentType.UniqueID]
    m.add predicate: "ToPredict",    types: [ArgumentType.UniqueID, ArgumentType.UniqueID]
    
    ///////////////////////////// rules ////////////////////////////////////
    def File geneFile = new File(this.args[0] + "gene.txt")
    def genes = []
    for (line in geneFile.readLines()) {
        genes << line.split("\t")[0]
    }
    
    def File drugFile = new File(this.args[0] + "drug.txt")
    def drugs = []
    for (line in drugFile.readLines()) {
        drugs << line.split("\t")[0]
    }

    def geneArg;
    for( String gene : genes ){
        geneArg = data.getUniqueID(gene);
        m.add rule : ( ToPredict(C, D) & ~DrugTarget(D, geneArg) & Essential(C, geneArg) ) >> ~Sensitive(C, D),  weight : 1, squared: false
    }

    m.add rule : ~Sensitive(C, D),  weight : 1
    
    println ""
    println "Rules with initial weights:"
    println m;
    println "fold ${i}"
    
    //////////////////////////// data setup ///////////////////////////
    // loads data
    def dir = this.args[0]
    def target_dir = "seed0" + java.io.File.separator + "cross_val_6fold" + java.io.File.separator;
    def evidencePartition = new Partition(0);
    
    insert = data.getInserter(DrugTarget, evidencePartition);
    InserterUtils.loadDelimitedData(insert, dir+"drug_target.txt");
    
    insert = data.getInserter(Essential, evidencePartition);
    InserterUtils.loadDelimitedDataTruth(insert, dir+"essential.txt");
   
    insert = data.getInserter(ToPredict, evidencePartition);
    InserterUtils.loadDelimitedData(insert, dir+target_dir+"fold${i}_train_to_predict.txt");
 
    // add target atoms
    def trainTargetPartition = new Partition(1);
    insert = data.getInserter(Sensitive, trainTargetPartition);
    InserterUtils.loadDelimitedData(insert, dir+target_dir+"fold${i}_train_to_predict.txt");
 

    Database db1 = data.getDatabase(trainTargetPartition, [DrugTarget, Essential, ToPredict] as Set, evidencePartition);
    
    //////////////////////////// weight learning ///////////////////////////
    Partition trueDataPartition = new Partition(2);
    insert = data.getInserter(Sensitive, trueDataPartition)
    InserterUtils.loadDelimitedDataTruth(insert, dir+target_dir+"fold${i}_train_truth.txt");
    
    Database trueDataDB = data.getDatabase(trueDataPartition, [Sensitive] as Set);
    MaxLikelihoodMPE weightLearning = new MaxLikelihoodMPE(m, db1, trueDataDB, config);
    weightLearning.learn();
    weightLearning.close();
    
    println ""
    println "Learned model:"
    println m

    trueDataDB.close();
        
    //////////////////////////// run inference with test data///////////////////////////
    def testEvidencePartition = new Partition(4);

    insert = data.getInserter(DrugTarget, testEvidencePartition);
    InserterUtils.loadDelimitedData(insert, dir+"drug_target.txt");

    insert = data.getInserter(Essential, testEvidencePartition);
    InserterUtils.loadDelimitedDataTruth(insert, dir+"essential.txt");

    insert = data.getInserter(ToPredict, testEvidencePartition);
    InserterUtils.loadDelimitedData(insert, dir+target_dir+"fold${i}_val_to_predict.txt");

    // add target atoms
    def testTargetPartition = new Partition(5);
    insert = data.getInserter(Sensitive, testTargetPartition);
    InserterUtils.loadDelimitedData(insert, dir+target_dir+"fold${i}_val_to_predict.txt");

    Database db2 = data.getDatabase(testTargetPartition, [DrugTarget, Essential, ToPredict] as Set, testEvidencePartition);

    MPEInference inferenceApp2 = new MPEInference(m, db2, config);
    inferenceApp2.mpeInference();
    inferenceApp2.close();

    println "saving inference results to result/"
    DecimalFormat formatter = new DecimalFormat("#.#######");
    def data_type = this.args[0].tokenize("/")[-1]

    def result_file = new File(result_path + "fold${i}_result.txt");
    result_file.write ""
    for (GroundAtom atom : Queries.getAllAtoms(db2, Sensitive)) {
        for (int i=0; i<2; i++) {
            result_file << atom.arguments[i].toString() + "\t"
        }
        result_file << formatter.format(atom.getValue()) + "\n"}
    
    // close the Databases to flush writes
    db2.close();
}
