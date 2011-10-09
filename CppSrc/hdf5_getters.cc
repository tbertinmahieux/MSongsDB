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


#include <iostream>
#include <string>

#include "H5Cpp.h"
#include "hdf5_getters.h"
using namespace H5;

// max characters of a field
//#define FIELDLEN 128

HDF5Getters::HDF5Getters(const char filename[]) {

  // open the file
  const H5std_string h5filename(filename);
  h5file = new H5File(h5filename, H5F_ACC_RDONLY);

  // create the 3 groups' names
  const H5std_string NAME_GROUP_METADATA("metadata");
  const H5std_string NAME_GROUP_ANALYSIS("analysis");
  const H5std_string NAME_GROUP_MUSICBRAINZ("musicbrainz");

  // open the 3 groups
  GROUP_METADATA = h5file->openGroup( NAME_GROUP_METADATA );
  GROUP_ANALYSIS = h5file->openGroup( NAME_GROUP_ANALYSIS );
  GROUP_MUSICBRAINZ = h5file->openGroup( NAME_GROUP_MUSICBRAINZ );

}

/*
 * Destructor
 */
HDF5Getters::~HDF5Getters() {
  // file
  delete h5file;
}

/*
 * Get Artist familiarity
 */
float HDF5Getters::get_artist_familiarity() const {
  return get_member_float( GROUP_METADATA, "artist_familiarity");
}


/* UTITITY FUNCTIONS */

/*
 * To get a float member from a given group;
 * dataset name is always 'songs'
 */
float HDF5Getters::get_member_float(const Group& group, 
				    const std::string name_member) const {
  const H5std_string MEMBER( name_member );
  const CompType mtype( sizeof(float) );
  mtype.insertMember( MEMBER, 0, PredType::NATIVE_FLOAT);
  DataSet dataset( group.openDataSet( "songs" ));
  float data_out = -1.;
  dataset.read( &data_out, mtype );
  return data_out;
}
