"""
Fun code to parse the list of papers from ISMIR exported to CSV.
Goal is to create a random paper generator for the website.
Therefore, we want authors, title (+link), year

Awful code! but awful CSV too....

T. Bertin-Mahieux (2010 Columbia University
tb2332@columbia.edu
"""


import os
import sys
import string

def die_with_usage():
    """ HELP MENU """
    print 'download the ISMIR list of papers in CSV format'
    print 'then:'
    print 'python ismir_csv_parser.py <ismircsv> <newtxtfile>'
    sys.exit(0)


if __name__ == '__main__':

    if len(sys.argv) < 3:
        die_with_usage()

    csvpath = sys.argv[1]
    txtpath = sys.argv[2]

    cnt = 0

    csv = open(csvpath,'r')
    txt = open(txtpath,'w')
    csv.readline() # skip header
    for line in csv.xreadlines():
        if line == '' or line.strip() == '':
            continue
        line = line.strip()
        # remove id
        pos = string.find(line,',')
        line = line[pos+1:]
        # get year
        year = line[2:6]
        pos = string.find(line,',')
        line = line[pos+1:]
        # authors
        pos = string.find(line,'<a')
        authors = line[:pos]
        authors = string.replace(authors,'";"',' ')
        authors = string.replace(authors,';;;',' and ')
        authors = string.replace(authors,'"','')
        authors = authors[:-1] # remove last comma
        line = line[pos:]
        # get link
        pos = string.find(line,'</a>')
        link = line[:pos+len('</a>')]
        link = string.replace(link,'";"',' ')
        link = string.replace(link,'""""','"')
        print 'year='+year,'authors='+authors,' link =',link
        # write to file
        txt.write(authors + ', ' + link + ', ' + year + '.\n')
        # cnt
        cnt += 1

    csv.close()
    txt.close()

    print cnt,'proper paper found!'
