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

#ifndef __HDF5_GETTERS__
#define __HDF5_GETTERS__

#include <iostream>
#include <string>

#include "H5Cpp.h"
//#include "hdf5_hl.h"
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
  h5file->close();
  delete h5file;
}

/*
 * Get Artist familiarity
 */
double HDF5Getters::get_artist_familiarity() const {
  return get_member_double( GROUP_METADATA, "artist_familiarity");
}

/*
 * Get Artist hotttnesss
 */
double HDF5Getters::get_artist_hotttnesss() const {
  return get_member_double( GROUP_METADATA, "artist_hotttnesss");
}

/*
 * Get Artist ID
 */
std::string HDF5Getters::get_artist_id() const {
  return get_member_str( GROUP_METADATA, "artist_id");
}

/*
 * Get Key
 */
int HDF5Getters::get_key() const {
  return get_member_int( GROUP_ANALYSIS, "key");
}


/*
 * Get Artist name
 */
std::string HDF5Getters::get_artist_name() const {
  return get_member_str( GROUP_METADATA, "artist_name");
}

/***************** UTITITY FUNCTIONS *******************/

/*
 * To get a double member from a given group;
 * dataset name is always 'songs'
 */
double HDF5Getters::get_member_double(const Group& group, const std::string name_member) {
  const H5std_string MEMBER( name_member );
  const CompType mtype( sizeof(double) );
  mtype.insertMember( MEMBER, 0, PredType::NATIVE_FLOAT);
  DataSet dataset( group.openDataSet( "songs" ));
  double data_out = -1.;
  dataset.read( &data_out, mtype );
  dataset.close();
  return data_out;
}

/*
 * To get a int member from a given group;
 * dataset name is always 'songs'
 */
int HDF5Getters::get_member_int(const Group& group, const std::string name_member) {
  const H5std_string MEMBER( name_member );
  const CompType mtype( sizeof(int) );
  mtype.insertMember( MEMBER, 0, PredType::NATIVE_INT);
  DataSet dataset( group.openDataSet( "songs" ));
  int data_out = -1;
  dataset.read( &data_out, mtype );
  dataset.close();
  return data_out;
}

/*
 * To get a string member from a given group;
 * dataset name is always 'songs'
 */
std::string HDF5Getters::get_member_str(const Group& group, const std::string name_member) {
  const H5std_string MEMBER( name_member );
  DataSet dataset( group.openDataSet( "songs" ));

  // Figuring out the proper string type is a mess.
  CompType datasetcomptype(dataset);
  int memberidx = datasetcomptype.getMemberIndex( MEMBER );
  DataType dtype = datasetcomptype.getMemberDataType( memberidx );
  const CompType mtype( (size_t) 1024 );
  mtype.insertMember( MEMBER, 0, dtype);

  // Need to figure out the proper size!
  // Otherwise, let's have a buffer that is always big enough...
  char buf[1024];
  dataset.read( (void*) buf, mtype );
  return std::string(buf);
  
}


#endif // __HDF5_GETTERS__
