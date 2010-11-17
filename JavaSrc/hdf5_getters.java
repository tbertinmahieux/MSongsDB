/*
Thierry Bertin-Mahieux (2010) Columbia University
tb2332@columbia.edu


This code contains a set of getters functions to access the fields
from an HDF5 song file (regular file with one song or summary file
with many songs) in Java.
The goal is to reproduce the Python getters behaviour.
Our aim is only to show how to use the HDF5 files with Java, the
code is not particularly optimized.

This is part of the Million Song Dataset project from
LabROSA (Columbia University) and The Echo Nest.


Copyright 2010, Thierry Bertin-Mahieux

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
*/

import ncsa.hdf.hdf5lib.*;

/**
 * Class containing static methods to open a HDF5 song file and access its content.
 */
public class hdf5_getters
{








    public static void main(String[] args)
    {
	if (args.length < 1)
	    {
		System.out.println("file 'hdf5_getters.java'");
		System.out.println("T. Bertin-Mahieux (2010) tb2332@columbia.edu");
		System.out.println("a util static class to read HDF5 song files from");
		System.out.println("the Million Songs Dataset project");
		System.out.println("demo:");
		System.out.println("   see README.txt to compile");
		System.out.println("   java hdf5_getters <some HDF5 song file>");
		System.exit(0);
	    }
    }

}