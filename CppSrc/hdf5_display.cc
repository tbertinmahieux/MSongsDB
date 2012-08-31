/*
 Thierry Bertin-Mahieux (2010) Columbia University
 tb2332@columbia.edu

 Demo code to display all fields of a given MSD HDF5 song file.

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
#include <stdlib.h>
#include <string.h>
#include "hdf5_getters.h"
using namespace std;

/*
 * Help menu
 */
void help_menu(void) {
  
  cout << "hdf5_display" << endl;
  cout << "    by T. Bertin-Mahieux (2011) Columbia U." << endl;
  cout << "       tb2332@columbia.edu" << endl;
  exit(0);
}


int main(int argc, const char* argv[]) {

  // help menu?
  if (argc < 2 || strcmp(argv[1],"help") == 0 || strcmp(argv[1],"-help") == 0)
    help_menu();

  // create wrapper
  HDF5Getters getters(argv[1]);
  
  // init values
  double dval;
  std::string sval;
  int ival;

  // print everything!
  dval = getters.get_artist_familiarity();
  cout << "artist familiarity: " << dval << endl;
  dval = getters.get_artist_hotttnesss();
  cout << "artist hotttnesss: " << dval << endl;
  sval = getters.get_artist_id();
  cout << "artist id: " << sval << endl;
  

  sval = getters.get_artist_name();
  cout << "artist name: " << sval << endl;
  ival = getters.get_key();
  cout << "key: " << ival << endl;


  return 0; // succesfully terminated
}
