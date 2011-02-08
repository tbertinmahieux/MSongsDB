/Tasks_Demos/YearPrediction/README.txt
    by T. Bertin-Mahieux (2010) Columbia University
       tb2332@columbia.edu

This folder contains all code related to year prediction, or era prediction
in general.

To start, look at tracks_per_year.txt in the addiontal files. 
If you don't have it already, look at the Million Song website.
This contains every tracks for which
we have the year information (based on musicbrainz) in ascending order.
The format is: year<SEP>track id<SEP>artist name<SEP>song title

We also provide a train/test split of artists, so everyone reports
similar results. In more details, prediction should be made for every
song of every test artist!
See artists_train.txt and artists_test.txt, and for details on how we
did the split: split_train_test.py


NOTE: some details are missing in this folder, we are preparing a submission
presenting the Million Song Dataset, and this will be the featured task.
The full code and results will soon be released, write us if you need them
sooner: Thierry Bertin-Mahieux, tb2332@columbia.edu   (January 2011)
