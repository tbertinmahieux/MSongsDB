/MSongsDB/Tasks_Demos/CoverSongs/waspaa11/README.txt

This folder contains the code to reproduce the result from:

"Large-scale cover song recognition using hashed chroma landmarks"
by T. Bertin-Mahieux and D. Ellis, WASPAA 2011

The code is provided "as is", with no guarantee whatsoever, under the GNU GPL 
license. From a research point of view, we do not claim that this represents
the state-of-the-art, please see it merely as a benchmark to compare your
own algoithm against.

If you have questions, first please read the paper. Then do not
hesitate to contact the authors.

Thierry Bertin-Mahieux
July 2011

******** REQUIREMENTS *************

We use python 2.6 with numpy installed on an Ubuntu machine.
We use pytables (http://www.pytables.org/) -> HDF5 wrapper.
We use coffee, and sometimes alcoholic beverages.


******** GETTING STARTED ***********

Here is how to reproduce results on the SHS dataset:

* for quick parameter testing (first result of the paper)
python quick_query_test.py /CoversSubsetData shs_dataset_train.txt

* create a database containing the fingerprints for the ~12k tracks
  of the SecondHandSongs dataset (using 2 threads)
  Here we have a directory with only the train songs from SHS.
python compute_hashcodes_mprocess.py /CoversSubsetData hashes.db 2

* add tables to the database, one per hashcode, in order to get
  track IDs that contain a given hashcode
python create_jcode_tables.py hashes.db

* now let's check covers from the SHS train dataset
  (this reproduces one of the first results from the paper)
python query_for_covers_mprocess.py hashes.db shs_dataset_train.txt output.h5 2

* to check the results, in python/ipython, the file 'output.h5' contains,
  under root/results you'll find:
  - query      track ID for which we want to find covers
  - target     track ID of a specific cover
  - pos        position (rank) of the target to the query
  - n_results  number of tracks with overlapping hashcodes with query
import numpy as np, tables
h5 = tables.openFile('./output.h5')
np.average(h5.root.results.pos[:])

Good luck,and enjoy!


******** IMPROVEMENTS ************

Starting at step 2, implementation is awful! We should not have used
SQL when all we needed was a lookup table.
Implement a keystore that, given an hashcode, gives you track IDs.
It could even fit in memory and be 100x faster!
Even a python dict() might do the job if you have enough RAM:
   {1131:[TR1234, TR456], 231231:[TR1234, TR789], ...}
