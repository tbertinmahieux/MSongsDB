/Tasks_Demos/YahooRatings/README.txt
      by Thierry Bertin-Mahieux (2011) Columbia University
         tb2332@columbia.edu


This folder contains code to link the Yahoo Ratings data
with the Million SOng Dataset

For Yahoo data:
http://webscope.sandbox.yahoo.com/

The most important code links Yahoo artist name with
Echo Nest artist ID from the Million Song Dataset
See: match_artist_names.py

We then count how many ratings these artists cover, see:
 count_ratings_known_artists.py
usage:
 python count_ratings_known_artists.py \
         /YahooData/R1/ydata-ymusic-artist-names-v1_0.txt \
         mapping_15780artists.txt \
         /YahooData/R1/ydata-ymusic-user-artist-ratings-v1_0.txt

Using the artist coverage as of January 10 2011, 
we cover 91% of the ratings (105215445/115579440 ratings)

MISSING ARTISTS
remember that you can use The Echo Nest API to get info and track
analysis for the artists not covered in the Million Song Dataset.
You even have the code to put these artists into this dataset format.

