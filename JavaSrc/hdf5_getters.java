/*
Thierry Bertin-Mahieux (2010) Columbia University
tb2332@columbia.edu


This code contains a set of getters functions to access the fields
from an HDF5 song file (regular file with one song or summary file
with many songs) in Java.
The goal is to reproduce the Python getters behaviour.
Our aim is only to show how to use the HDF5 files with Java, the
code is not optimized at all!

To get a faster code, you should load metadata/songs and analysis/songs
only once, see the Matlab code in /MatlabSrc for inspiration.

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

import ncsa.hdf.hdf5lib.exceptions.HDF5Exception;
//import ncsa.hdf.hdf5lib.*;
import ncsa.hdf.object.HObject;
import ncsa.hdf.object.Datatype;
import ncsa.hdf.object.Dataset;
import ncsa.hdf.object.h5.*;
import java.util.Vector;
import java.util.Arrays;


/**
 * Class containing static methods to open a HDF5 song file and access its content.
 */
public class hdf5_getters
{

    /**
     * Opens an existing HDF5 file with read only access.
     */
    public static H5File hdf5_open_readonly(String filename)
    {
	return new H5File(filename,H5File.READ);
    }

    /**
     * Closes the HDF5 file.
     * Function usefull only because of the try/catch
     */
    public static void hdf5_close(H5File h5) 
    {
	try {
	    h5.close();
	} catch (HDF5Exception ex) {
	    System.out.println("Could not close HDF5 file?");
	    ex.printStackTrace();
	}
    }
 
    public static int get_num_songs(H5File h5)
    {
	H5CompoundDS metadata;
	try {
	    metadata = (H5CompoundDS) h5.get("/metadata/songs");
	    metadata.init();
	    return metadata.getHeight();
	} catch (Exception e) {
	    e.printStackTrace();
	    return -1;
	}
    }

    public static double get_artist_familiarity(H5File h5) throws Exception {
	return get_artist_familiarity(h5, 0); }
    public static double get_artist_familiarity(H5File h5, int songidx) throws Exception
    {    
	H5CompoundDS metadata = (H5CompoundDS) h5.get("/metadata/songs");
	metadata.init();
	int wantedMember = find( metadata.getMemberNames() , "artist_familiarity");
	assert(wantedMember >= 0);		
	Vector alldata = (Vector) metadata.getData();
	double[] col = (double[]) alldata.get(wantedMember);
	return col[songidx];
    }

    public static double get_artist_hotttnesss(H5File h5) throws Exception {
	return get_artist_hotttnesss(h5, 0); }
    public static double get_artist_hotttnesss(H5File h5, int songidx) throws Exception
    {    
	H5CompoundDS metadata = (H5CompoundDS) h5.get("/metadata/songs");
	metadata.init();
	int wantedMember = find( metadata.getMemberNames() , "artist_hotttnesss");
	assert(wantedMember >= 0);		
	Vector alldata = (Vector) metadata.getData();
	double[] col = (double[]) alldata.get(wantedMember);
	return col[songidx];
    }

    public static String get_artist_id(H5File h5) throws Exception {
	return get_artist_id(h5, 0); }
    public static String get_artist_id(H5File h5, int songidx) throws Exception
    {    
	H5CompoundDS metadata = (H5CompoundDS) h5.get("/metadata/songs");
	metadata.init();
	int wantedMember = find( metadata.getMemberNames() , "artist_id");
	assert(wantedMember >= 0);		
	Vector alldata = (Vector) metadata.getData();
	String[] col = (String[]) alldata.get(wantedMember);
	return col[songidx];
    }

    public static double get_artist_latitude(H5File h5) throws Exception {
	return get_artist_latitude(h5, 0); }
    public static double get_artist_latitude(H5File h5, int songidx) throws Exception
    {    
	H5CompoundDS metadata = (H5CompoundDS) h5.get("/metadata/songs");
	metadata.init();
	int wantedMember = find( metadata.getMemberNames() , "artist_latitude");
	assert(wantedMember >= 0);		
	Vector alldata = (Vector) metadata.getData();
	double[] col = (double[]) alldata.get(wantedMember);
	return col[songidx];
    }

    public static double get_artist_longitude(H5File h5) throws Exception {
	return get_artist_longitude(h5, 0); }
    public static double get_artist_longitude(H5File h5, int songidx) throws Exception
    {    
	H5CompoundDS metadata = (H5CompoundDS) h5.get("/metadata/songs");
	metadata.init();
	int wantedMember = find( metadata.getMemberNames() , "artist_longitude");
	assert(wantedMember >= 0);		
	Vector alldata = (Vector) metadata.getData();
	double[] col = (double[]) alldata.get(wantedMember);
	return col[songidx];
    }

    public static String get_artist_location(H5File h5) throws Exception {
	return get_artist_location(h5, 0); }
    public static String get_artist_location(H5File h5, int songidx) throws Exception
    {    
	H5CompoundDS metadata = (H5CompoundDS) h5.get("/metadata/songs");
	metadata.init();
	int wantedMember = find( metadata.getMemberNames() , "artist_location");
	assert(wantedMember >= 0);		
	Vector alldata = (Vector) metadata.getData();
	String[] col = (String[]) alldata.get(wantedMember);
	return col[songidx];
    }

    public static String get_artist_name(H5File h5) throws Exception {
	return get_artist_name(h5, 0); }
    public static String get_artist_name(H5File h5, int songidx) throws Exception
    {    
	H5CompoundDS metadata = (H5CompoundDS) h5.get("/metadata/songs");
	metadata.init();
	int wantedMember = find( metadata.getMemberNames() , "artist_name");
	assert(wantedMember >= 0);		
	Vector alldata = (Vector) metadata.getData();
	String[] col = (String[]) alldata.get(wantedMember);
	return col[songidx];
    }

    public static double get_song_hotttnesss(H5File h5) throws Exception {
	return get_song_hotttnesss(h5, 0); }
    public static double get_song_hotttnesss(H5File h5, int songidx) throws Exception
    {    
	H5CompoundDS metadata = (H5CompoundDS) h5.get("/metadata/songs");
	metadata.init();
	int wantedMember = find( metadata.getMemberNames() , "song_hotttnesss");
	assert(wantedMember >= 0);		
	Vector alldata = (Vector) metadata.getData();
	double[] col = (double[]) alldata.get(wantedMember);
	return col[songidx];
    }

    public static String get_title(H5File h5) throws Exception {
	return get_title(h5, 0); }
    public static String get_title(H5File h5, int songidx) throws Exception
    {    
	H5CompoundDS metadata = (H5CompoundDS) h5.get("/metadata/songs");
	metadata.init();
	int wantedMember = find( metadata.getMemberNames() , "title");
	assert(wantedMember >= 0);		
	Vector alldata = (Vector) metadata.getData();
	String[] col = (String[]) alldata.get(wantedMember);
	return col[songidx];
    }

    public static double get_duration(H5File h5) throws Exception {
	return get_duration(h5, 0); }
    public static double get_duration(H5File h5, int songidx) throws Exception
    {    
	H5CompoundDS analysis = (H5CompoundDS) h5.get("/analysis/songs");
	analysis.init();
	int wantedMember = find( analysis.getMemberNames() , "duration");
	assert(wantedMember >= 0);		
	Vector alldata = (Vector) analysis.getData();
	double[] col = (double[]) alldata.get(wantedMember);
	return col[songidx];
    }

    public static double get_end_of_fade_in(H5File h5) throws Exception {
	return get_end_of_fade_in(h5, 0); }
    public static double get_end_of_fade_in(H5File h5, int songidx) throws Exception
    {    
	H5CompoundDS analysis = (H5CompoundDS) h5.get("/analysis/songs");
	analysis.init();
	int wantedMember = find( analysis.getMemberNames() , "end_of_fade_in");
	assert(wantedMember >= 0);		
	Vector alldata = (Vector) analysis.getData();
	double[] col = (double[]) alldata.get(wantedMember);
	return col[songidx];
    }

    public static int get_key(H5File h5) throws Exception {
	return get_key(h5, 0); }
    public static int get_key(H5File h5, int songidx) throws Exception
    {    
	H5CompoundDS analysis = (H5CompoundDS) h5.get("/analysis/songs");
	analysis.init();
	int wantedMember = find( analysis.getMemberNames() , "key");
	assert(wantedMember >= 0);		
	Vector alldata = (Vector) analysis.getData();
	int[] col = (int[]) alldata.get(wantedMember);
	return col[songidx];
    }

    public static double get_key_confidence(H5File h5) throws Exception {
	return get_key_confidence(h5, 0); }
    public static double get_key_confidence(H5File h5, int songidx) throws Exception
    {    
	H5CompoundDS analysis = (H5CompoundDS) h5.get("/analysis/songs");
	analysis.init();
	int wantedMember = find( analysis.getMemberNames() , "key_confidence");
	assert(wantedMember >= 0);		
	Vector alldata = (Vector) analysis.getData();
	double[] col = (double[]) alldata.get(wantedMember);
	return col[songidx];
    }
 
    public static double get_loudness(H5File h5) throws Exception {
	return get_loudness(h5, 0); }
    public static double get_loudness(H5File h5, int songidx) throws Exception
    {    
	H5CompoundDS analysis = (H5CompoundDS) h5.get("/analysis/songs");
	analysis.init();
	int wantedMember = find( analysis.getMemberNames() , "loudness");
	assert(wantedMember >= 0);		
	Vector alldata = (Vector) analysis.getData();
	double[] col = (double[]) alldata.get(wantedMember);
	return col[songidx];
    }

    public static int get_mode(H5File h5) throws Exception {
	return get_mode(h5, 0); }
    public static int get_mode(H5File h5, int songidx) throws Exception
    {    
	H5CompoundDS analysis = (H5CompoundDS) h5.get("/analysis/songs");
	analysis.init();
	int wantedMember = find( analysis.getMemberNames() , "mode");
	assert(wantedMember >= 0);		
	Vector alldata = (Vector) analysis.getData();
	int[] col = (int[]) alldata.get(wantedMember);
	return col[songidx];
    }

    public static double get_mode_confidence(H5File h5) throws Exception {
	return get_mode_confidence(h5, 0); }
    public static double get_mode_confidence(H5File h5, int songidx) throws Exception
    {    
	H5CompoundDS analysis = (H5CompoundDS) h5.get("/analysis/songs");
	analysis.init();
	int wantedMember = find( analysis.getMemberNames() , "mode_confidence");
	assert(wantedMember >= 0);		
	Vector alldata = (Vector) analysis.getData();
	double[] col = (double[]) alldata.get(wantedMember);
	return col[songidx];
    }

    public static double get_start_of_fade_out(H5File h5) throws Exception {
	return get_start_of_fade_out(h5, 0); }
    public static double get_start_of_fade_out(H5File h5, int songidx) throws Exception
    {    
	H5CompoundDS analysis = (H5CompoundDS) h5.get("/analysis/songs");
	analysis.init();
	int wantedMember = find( analysis.getMemberNames() , "start_of_fade_out");
	assert(wantedMember >= 0);		
	Vector alldata = (Vector) analysis.getData();
	double[] col = (double[]) alldata.get(wantedMember);
	return col[songidx];
    }

    public static double get_tempo(H5File h5) throws Exception {
	return get_tempo(h5, 0); }
    public static double get_tempo(H5File h5, int songidx) throws Exception
    {    
	H5CompoundDS analysis = (H5CompoundDS) h5.get("/analysis/songs");
	analysis.init();
	int wantedMember = find( analysis.getMemberNames() , "tempo");
	assert(wantedMember >= 0);		
	Vector alldata = (Vector) analysis.getData();
	double[] col = (double[]) alldata.get(wantedMember);
	return col[songidx];
    }

    public static int get_time_signature(H5File h5) throws Exception {
	return get_time_signature(h5, 0); }
    public static int get_time_signature(H5File h5, int songidx) throws Exception
    {    
	H5CompoundDS analysis = (H5CompoundDS) h5.get("/analysis/songs");
	analysis.init();
	int wantedMember = find( analysis.getMemberNames() , "time_signature");
	assert(wantedMember >= 0);		
	Vector alldata = (Vector) analysis.getData();
	int[] col = (int[]) alldata.get(wantedMember);
	return col[songidx];
    }

    public static double get_time_signature_confidence(H5File h5) throws Exception {
	return get_time_signature_confidence(h5, 0); }
    public static double get_time_signature_confidence(H5File h5, int songidx) throws Exception
    {    
	H5CompoundDS analysis = (H5CompoundDS) h5.get("/analysis/songs");
	analysis.init();
	int wantedMember = find( analysis.getMemberNames() , "time_signature_confidence");
	assert(wantedMember >= 0);		
	Vector alldata = (Vector) analysis.getData();
	double[] col = (double[]) alldata.get(wantedMember);
	return col[songidx];
    }

    // TO DO: ADD ARRAY GETTERS

    /**
     * Slow utility function.
     */
    public static int find(String[] tab, String key)
    {
	for (int k = 0; k < tab.length; k++)
	    if (tab[k].equals(key)) return k;
	return -1;
    }


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
	String filename = args[0];
	System.out.println("file: " + filename);
	H5File h5 = hdf5_open_readonly(filename);
	int nSongs = get_num_songs(h5);
	System.out.println("numberof songs: " + nSongs);
	if (nSongs > 1) System.out.println("we'll display infor for song 0");
	try {
	    System.out.println("artist familiarity: " + get_artist_familiarity(h5));
	    System.out.println("artist hotttnesss: " + get_artist_hotttnesss(h5));
	    System.out.println("artist id: " + get_artist_id(h5));
	    System.out.println("artist latitude: " + get_artist_latitude(h5));
	    System.out.println("artist longitude: " + get_artist_longitude(h5));
	    System.out.println("artist location: " + get_artist_location(h5));
	    System.out.println("artist name: " + get_artist_name(h5));
	    System.out.println("song hotttnesss: " + get_song_hotttnesss(h5));
	    System.out.println("title: " + get_title(h5));
	    System.out.println("duration: " + get_duration(h5));
	    System.out.println("end_of_fade_in: " + get_end_of_fade_in(h5));
	    System.out.println("key: " + get_key(h5));
	    System.out.println("key confidence: " + get_key_confidence(h5));
	    System.out.println("loudness: " + get_loudness(h5));
	    System.out.println("mode: " + get_mode(h5));
	    System.out.println("mode confidence: " + get_mode_confidence(h5));
	    System.out.println("start of fade out: " + get_start_of_fade_out(h5));
	    System.out.println("tempo: " + get_tempo(h5));
	    System.out.println("time signature: " + get_time_signature(h5));
	    System.out.println("time signature confidence: " + get_time_signature_confidence(h5));
	} catch (Exception e) {
	    System.out.println("something went wrong:");
	    e.printStackTrace();
	}
	hdf5_close(h5);
	System.out.println("done, file closed.");
    }

}