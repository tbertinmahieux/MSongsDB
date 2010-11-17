Million Song Dataset
JavaSrc/README.txt
tb2332@columbia.edu

You must have install the HDF5 library.
You also need the JAVA HDF5 jar files for your operating system, details at:
http://www.hdfgroup.org/hdf-java-html/hdf-object/index.html
Specifically: jhdf5.jar  jhdf5obj.jar  jhdfobj.jar  

To compile (could be simplified) and run the java demo, do (on Linux):

cd <blablabla/JavaSrc>
javac -classpath jhdf5.jar:jhdf5obj.jar:jhdfobj.jar hdf5_getters.java
java -classpath ./jhdf5.jar:./jhdf5obj.jar:./jhdfobj.jar:. hdf5_getters
