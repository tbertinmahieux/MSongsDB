/Tasks_Demos/ArtistRecognition/README.txt
    by T. Bertin-Mahieux (2010) Columbia University
       tb2332@columbia.edu

This folder contains all code related to artist recognition.

REMINDER:
 - the dataset contains 44,745 unique artists based on their Echo Nest ID
 - out of that, 180,073 have at least 20 songs.


TWO SPLITS? WHAT IS THE DIFFERENCE?
Both only look at artists with at least 20 songs. Differences are:
- in the regular split, each artist has 15 songs in the training set,
the rest is in the testing set.
- in the unbalanced split, each artist has 2/3 of his songs in the training
set, the rest in the testing set. It makes things easier because 1) the
training set is larger and 2) you can use a non uniform prior on the artists.
