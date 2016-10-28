#! /bin/bash
echo "compiling silently......"
mvn -q compile
echo "build classpath just as silently......"
mvn -q dependency:build-classpath -Dmdep.outputFile=classpath.out
echo "====================== mighty result seperator ======================="
java -cp ./target/classes:`cat classpath.out` edu.ucsc.FirstModel 5
java -cp ./target/classes:`cat classpath.out` edu.ucsc.FirstModelActiveRule 5
java -cp ./target/classes:`cat classpath.out` edu.ucsc.FirstModelEssentialRule 5
#java -cp ./target/classes:`cat classpath.out` edu.ucsc.SecondModel 5
#java -cp ./target/classes:`cat classpath.out` edu.ucsc.SecondModelEssentialRule 5
#java -cp ./target/classes:`cat classpath.out` edu.ucsc.SecondModelActiveRule 5
