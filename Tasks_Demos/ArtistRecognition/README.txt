/Tasks_Demos/ArtistRecognition/README.txt
    by T. Bertin-Mahieux (2010) Columbia University
       tb2332@columbia.edu

This folder contains all code related to artist recognition.

REMINDER:
 - the dataset contains 44,745 unique artists based on their Echo Nest ID
 - out of that, 18,073 have at least 20 songs.


TWO SPLITS? WHAT IS THE DIFFERENCE?
Both only look at artists with at least 20 songs. Differences are:
- in the regular split, each artist has 15 songs in the training set,
the rest is in the testing set.
- in the unbalanced split, each artist has 2/3 of his songs in the training
set, the rest in the testing set. It makes things easier because 1) the
training set is larger and 2) you can use a non uniform prior on the artists.

INCLUDE ALL ARTISTS?
when we do KNN, if our KNN model includes all existing artists,
it is obviously easier to mistake a test artist.
In our code, use -onlytesta flag to train only on artists that are in the
test set.

BENCHMARK

easy case: unbalanced split, train only on test artists
           - best constant predictor (always same artist): 69/261503=0.026%
           - using our K-nn model (K=1)   9.578%

difficult case: balanced split, train on all artists
           - best contant predictor       193/532300=0.036%
	   - using our K-nn model (K=1)   4.82%


CODE TO REPRODUCE THE K-NN BENCHMARK EXPERIMENTS
easy case:
python process_train_set.py -onlytesta -nthreads 5 MillionSong/data ArtistRecognition/songs_test_unbalanced.txt track_metadata.db trained_knn_unbalanced.h5
(2h30m)
python process_test_set.py -nthreads MillionSong/data trained_knn_unbalanced.h5 ArtistRecognition/songs_test_unbalanced.txt track_metadata.db
(2h10m)
difficult case:
python process_train_set.py -nthreads 5 MillionSong/data ArtistRecognition/songs_test.txt track_metadata.db trained_knn.h5
(2h10m)
python process_test_set.py -nthreads MillionSong/data trained_knn.h5 ArtistRecognition/songs_test.txt track_metadata.db
(4h30m)
