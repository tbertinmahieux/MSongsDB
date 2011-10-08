# Thierry Bertin-Mahieux (2010) Columbia University
# tb2332@columbia.edu
#
# Makefile for the C++ HDF5 wrapper code
#
# This is part of the Million Song Dataset project from
# LabROSA (Columbia University) and The Echo Nest.
#
#
# Copyright 2011, Thierry Bertin-Mahieux
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# compiler
CC=g++
# options passed to the compiler
CFLAGS=-c -Wall


all: hdf5_wrapper.o
#$(CC) $(CFLAGS) hdf5_display.cpp -o hdf5_display

hdf5_wrapper.o:
	$(CC) $(CFLAGS) -c hdf5_wrapper.cc

clean:
	rm -rf *.o #hdf5_display