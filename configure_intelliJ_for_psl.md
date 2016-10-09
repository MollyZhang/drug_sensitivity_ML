##To configure intelliJ IDEA IDE for PSL project:

#### Download and install intelliJ from https://www.jetbrains.com/idea/#chooseYourEdition

#### Configure Maven PSL project with Groovy support in intelliJ
    Open IntelliJ IDEA
    File -> new -> Project -> Select "Maven" from left panel
    On the right side of the window, choose Project SDK (java version 1.8.*)
    Click checkbox "Create from archetype", and then click "Add Archetype..."
    In "Add Archetype" Window that appeared, fill in the following and click ok
      GroupId: edu.umd.cs
      ArtifactId: psl-archetype-groovy
      Version: 1.2.1
      Respository(optional): https://scm.umiacs.umd.edu/maven/lccd/content/repositories/psl-releases/
    Choose the new archetype that's been added: edu.umd.cs:psl-archetype-groovy, click next
    Fill "edu.ucsc" in GroupId and "cancer" in ArtifactId, click next
    Do nothing at the next window, click next
    Fill "intelliJ-psl" in Project name, click Finish
    In the intelliJ project window, right click on project name ("IntelliJ-psl"), click "Add Framework Support..."
    Check the checkbox next to "Groovy", click OK

#### Done!

#### Note: an oddity with intelliJ is that the file paths in scripts has to be absolute path for the file to be found 
    
