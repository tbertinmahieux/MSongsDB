/tasks/Preview7digital/README.txt

T. Bertin-Mahieux (2010) Columbia University
tb2332@columbia.edu

Simple code to get a url preview from 7digital.com for
a given track in the Million Song Dataset project.
This could be incorporated in a user study experiment,
or as a debugging tool (is this song really that 'rock'?),
etc.

You need a 7digital API key, available at:
http://access.7digital.com/partnerprogram
we recommend you put the key as a environment variable:
DIGITAL7_API_KEY

In general, 7digital developer's website is:
http://developer.7digital.net/

We are aware of a python wrapper around 7digital API (thanks Oscar!):
https://github.com/ocelma/7-digital
To be as general as possible, we intend not to use it, but
we do recommend its use in a real application!

PLAYER
------
We are building a graphical player, see player_7digital.py
It is in development, but the basic functionnalities are there.
It takes a track or song ID, or an artist/title as input.
It is Linux-dependent for the moment, but it should be ready
for Mac soon.
It depends on Tkinter, pyao and pymad. If you can install these,
you can make it work, write us if you need help or want to suggest
features.

MATLAB
------
Dan Ellis provided a Matlab version of the script, see MatlabSrc directory
at the top level of this repository, script name: load_preview.m
