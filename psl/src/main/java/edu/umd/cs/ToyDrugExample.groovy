//    impliment basic commandline psl example

package edu.umd.cs.example;

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

////////////////////////// initial setup ////////////////////////
ConfigManager cm = ConfigManager.getManager()
ConfigBundle config = cm.getBundle("basic-example")

def defaultPath = System.getProperty("java.io.tmpdir")
String dbpath = config.getString("dbpath", defaultPath + File.separator + "basic-example")
DataStore data = new RDBMSDataStore(new H2DatabaseDriver(Type.Disk, dbpath, true), config)
PSLModel m = new PSLModel(this, data)

////////////////////////// predicate declaration ////////////////////////
m.add predicate: "Person",       types: [ArgumentType.UniqueID, ArgumentType.String]
m.add predicate: "Location",     types: [ArgumentType.UniqueID, ArgumentType.String]
m.add predicate: "Knows",        types: [ArgumentType.UniqueID, ArgumentType.UniqueID]
m.add predicate: "Lives",        types: [ArgumentType.UniqueID, ArgumentType.UniqueID]

///////////////////////////// rules ////////////////////////////////////
m.add rule : ( Knows(P1, P2) & Lives(P1, L) ) >> Lives(P2, L),  weight : 10
m.add rule : ( Knows(P2, P1) & Lives(P1, L) ) >> Lives(P2, L),  weight : 10
m.add rule: ~Lives(P, L), weight: 2

println m;

//////////////////////////// data setup ///////////////////////////
// loads data
def dir = 'data'+java.io.File.separator+'cli'+java.io.File.separator;
def evidencePartition = new Partition(0);

insert = data.getInserter(Person, evidencePartition);
InserterUtils.loadDelimitedData(insert, dir+"person.txt");

insert = data.getInserter(Location, evidencePartition);
InserterUtils.loadDelimitedData(insert, dir+"location.txt");

insert = data.getInserter(Knows, evidencePartition);
InserterUtils.loadDelimitedData(insert, dir+"knows.txt");

insert = data.getInserter(Lives, evidencePartition);
InserterUtils.loadDelimitedData(insert, dir+"lives.txt");

// add target atoms
def targetPartition = new Partition(1);
insert = data.getInserter(Lives, targetPartition);
InserterUtils.loadDelimitedData(insert, dir+"lives_targets.txt");


Database db = data.getDatabase(targetPartition, [Person, Location, Knows] as Set, evidencePartition);

//////////////////////////// run inference ///////////////////////////
MPEInference inferenceApp = new MPEInference(m, db, config);
inferenceApp.mpeInference();
inferenceApp.close();

println "Inference results with hand-defined weights:"
DecimalFormat formatter = new DecimalFormat("#.##");
for (GroundAtom atom : Queries.getAllAtoms(db, Person))
    println atom.toString() + "\t" + formatter.format(atom.getValue());

for (GroundAtom atom : Queries.getAllAtoms(db, Location))
    println atom.toString() + "\t" + formatter.format(atom.getValue());

for (GroundAtom atom : Queries.getAllAtoms(db, Knows))
    println atom.toString() + "\t" + formatter.format(atom.getValue());

for (GroundAtom atom : Queries.getAllAtoms(db, Lives))
    println atom.toString() + "\t" + formatter.format(atom.getValue());


/*

//////////////////////////// weight learning ///////////////////////////
Partition trueDataPartition = new Partition(2);
insert = data.getInserter(SamePerson, trueDataPartition)
InserterUtils.loadDelimitedDataTruth(insert, dir + "sn_align.txt");

Database trueDataDB = data.getDatabase(trueDataPartition, [samePerson] as Set);
MaxLikelihoodMPE weightLearning = new MaxLikelihoodMPE(m, db, trueDataDB, config);
weightLearning.learn();
weightLearning.close();

println ""
println "Learned model:"
println m

// close the Databases to flush writes
db.close();
trueDataDB.close();
*/
