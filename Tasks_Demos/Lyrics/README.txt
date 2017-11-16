/Tasks_Demos/Lyrics/README.txt
   by T. Bertin-Mahieux (2011) Columbia University
      tb2332@columbia.edu

This folder contains code to deal with the musiXmatch dataset,
the official collection of lyrics for the Million Song Dataset.
See:
  http://labrosa.ee.columbia.edu/millionsong/musixmatch

The mXm dataset comes in 2 text files, train and test.

To simplify its usage, we also provide a SQLite database with the
same data. The code to recreate this database is:
   mxm_dataset_to_db.py
More details on the database:
   - it contains two tables, 'words' and 'lyrics'
   - table 'words' has one column: 'word'. Words are entered according
     to popularity, check their ROWID if you want to check their position.
     ROWID is an implicit column in SQLite, it starts at 1.
   - table 'lyrics' contains 5 columns, see below
   - column 'track_id' -> as usual, track id from the MSD
   - column 'mxm_tid' -> track ID from musiXmatch
   - column 'word' -> a word that is also in the 'words' table
   - column 'count' -> word count for the word
   - column 'is_test' -> 0 if this example is from the train set, 1 if test

If you want to know exactly how we created the bag-of-wirds, look at:
  lyrics_to_bow.py
Note that it requires the following Python package:
  http://pypi.python.org/pypi/stemming/1.0

Please enjoy, and don't hesitate to give us feedback!
