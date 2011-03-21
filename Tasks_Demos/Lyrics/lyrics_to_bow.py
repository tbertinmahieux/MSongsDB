#!/usr/bin/env python
"""
Thierry Bertin-Mahieux (2011) Columbia University
tb2332@columbia.edu

This code shows how we created bag of words for the musiXmatch
dataset. I has a command line interface, but it is mostly a library
with one main function.

This is part of the Million Song Dataset project from
LabROSA (Columbia University) and The Echo Nest.
http://labrosa.ee.columbia.edu/millionsong/

Copyright 2011, Thierry Bertin-Mahieux

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import os
import sys
try:
    from stemming.porter2 import stem
except ImportError:
    print 'You need to install the following stemming package:'
    print 'http://pypi.python.org/pypi/stemming/1.0'
    sys.exit(0)


def lyrics_to_bow(lyrics):
    """
    Main function to stem and create bag of words.
    It is what we used for the musiXmatch dataset.
    It is heavily oriented towards English lyrics, we apologize for that.
    INPUT
        lyrics as a string
    RETURN
        dictionary word -> count
        or None if something was wrong (e.g. not enough words)
    """
    # remove end of lines
    lyrics_flat = lyrics.replace('\r', '\n').replace('\n', ' ').lower()
    lyrics_flat = ' ' + lyrics_flat + ' '
    # special cases (English...)
    lyrics_flat = lyrics_flat.replace("'m ", " am ")
    lyrics_flat = lyrics_flat.replace("'re ", " are ")
    lyrics_flat = lyrics_flat.replace("'ve ", " have ")
    lyrics_flat = lyrics_flat.replace("'d ", " would ")
    lyrics_flat = lyrics_flat.replace("'ll ", " will ")
    lyrics_flat = lyrics_flat.replace(" he's ", " he is ")
    lyrics_flat = lyrics_flat.replace(" she's ", " she is ")
    lyrics_flat = lyrics_flat.replace(" it's ", " it is ")
    lyrics_flat = lyrics_flat.replace(" ain't ", " is not ")
    lyrics_flat = lyrics_flat.replace("n't ", " not ")
    lyrics_flat = lyrics_flat.replace("'s ", " ")
    # remove boring punctuation and weird signs
    punctuation = (',', "'", '"', ",", ';', ':', '.', '?', '!', '(', ')',
                   '{', '}', '/', '\\', '_', '|', '-', '@', '#', '*')
    for p in punctuation:
        lyrics_flat = lyrics_flat.replace(p, '')
    words = filter(lambda x: x.strip() != '', lyrics_flat.split(' '))
    # stem words
    words = map(lambda x: stem(x), words)
    bow = {}
    for w in words:
        if not w in bow.keys():
            bow[w] = 1
        else:
            bow[w] += 1
    # remove special words that are wrong
    fake_words = ('>', '<', 'outro~')
    bowwords = bow.keys()
    for bw in bowwords:
        if bw in fake_words:
            bow.pop(bw)
        elif bw.find(']') >= 0:
            bow.pop(bw)
        elif bw.find('[') >= 0:
            bow.pop(bw)
    # not big enough? remove instrumental ones among others
    if len(bow) <= 3:
        return None
    # done
    return bow


def die_with_usage():
    """ HELP MENU """
    print 'lyrics_to_bow.py'
    print '   by T. Bertin-Mahieux (2011) Columbia University'
    print '      tb2332@columbia.edu'
    print 'This code shows how we transformed lyrics into bag-of-words.'
    print 'It is mostly intended to be used as a library, but you can pass'
    print 'in lyrics and we print the resulting dictionary.'
    print ''
    print 'USAGE:'
    print '  ./lyrics_to_bow.py <lyrics>'
    print 'PARAMS:'
    print '    <lyrics>  - lyrics as one string'
    sys.exit(0)


if __name__ == '__main__':

    # help menu
    if len(sys.argv) < 2:
        die_with_usage()

    # params (lyrics)
    lyrics = ''
    for word in sys.argv[2:]:
        lyrics += ' ' + word
    lyrics = lyrics.strip()

    # make bag of words
    bow = lyrics_to_bow(lyrics)
    if bow is None:
        print 'ERROR, maybe there was not enough words to be realistic?'
        sys.exit(0)

    # print result
    try:
        from operator import itemgetter
        print sorted(bow.items(), key=itemgetter(1), reverse=True)
    except ImportError:
        print bow
