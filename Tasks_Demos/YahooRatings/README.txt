/Tasks_Demos/YahooRatings/README.txt
      by Thierry Bertin-Mahieux (2011) Columbia University
         tb2332@columbia.edu


THis folder contains code to link the Yahoo Ratings data
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
         /YahooData/Webscope_R1/ydata-ymusic-artist-names-v1_0.txt \
         mapping_15780artists.txt \
         /YahooData/Webscope_R1/ydata-ymusic-user-artist-ratings-v1_0.txt
