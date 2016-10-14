#! /bin/bash
echo "compiling silently......"
mvn -q compile
echo "build classpath just as silently......"
mvn -q dependency:build-classpath -Dmdep.outputFile=classpath.out
echo "====================== mighty result seperator ======================="
java -cp ./target/classes:`cat classpath.out` edu.ucsc.$1 $2
