
/MSongsDB/Tasks_Demos/YearPrediction/ismir11/README.txt

Code to reproduce the experiments on year prediction from the paper:

The Million Song Dataset
by T. Bertin-Mahieux, D. Ellis, B. Whitman and P. Lamere
ISMIR 2011

The code is shared under the GNU GPL license.

Enjoy, and please write us if you have questions!

Thierry Bertin-Mahieux
tb2332@columbia.edu


********* REQUIREMENTS *********

We use python 2.6 with numpy on an Ubuntu machine.
We installed the great Vowpal Wabbit (http://hunch.net/~vw/).
We dance in circle for the full moon.


********* EXPERIMENTS **********

The paper contains 3 main results:
- no audio features, i.e. best constant predictor
- kNN, slow and poor results
- vw, fast and better results

****************
** no features:

* simply launch:
python year_pred_benchmark.py ../artists_test.txt track_metadata.db

****************
** kNN:

* 'train' the model, e.g. save a bunch of examples
  look at the flags to set parameters like number
  of threads, window size, ...
  as we said, it is slow, and not great
python process_train_set.py -testartists ../artists_test.txt /MSD/data model.h5

* test it.
  if you set flags during training, make sure you
  have the same during testing
  numerical results will be output.
python process_test_set.py /MSD/data model.h5 ../artists_test.txt track_metadata.db

* measure


****************
** vowpal wabbit:

* create the dataset using:
python create_vw_dataset.py /MSD/data ../artists_test.txt track_metadata.db vw_train.txt vw_test.txt

* test many vw settings using the following script.
  some values to set at the top.
python auto_vw.py

* or just launch vw using the parameters we give in the paper
  measure the result with the following
python measure_vw_res.py vw_test.txt vwoutput
