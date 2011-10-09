/** 
 Thierry Bertin-Mahieux (2010) Columbia University
 tb2332@columbia.edu

 Code to access fields of a MSD HDF5 song file.

 This is part of the Million Song Dataset project from
 LabROSA (Columbia University) and The Echo Nest.


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
*/

#include <vector>
#include <string>

#include "H5Cpp.h"
using namespace H5;

// max characters of a field
#define FIELDLEN 128

class HDF5Getters {

 private:
  
  // file
  H5File* h5file;

  // the 3 groups
  Group GROUP_METADATA;
  Group GROUP_ANALYSIS;
  Group GROUP_MUSICBRAINZ;

  // utility function
  float get_member_float(const Group& group, const std::string name_member) const;


 public:

  // constructor
  HDF5Getters(const char filename[]);

  // destructor
  ~HDF5Getters();

  // get the number of songs
  int get_num_songs() const;

  // get artist familiarity
  float get_artist_familiarity() const;

};
