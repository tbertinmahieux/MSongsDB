%% msd_intro_matlab - Million Song Dataset from Matlab
%
% This code provides a quick introduction to the Million Song
% Dataset and how to access and manipulate it from Matlab.  For
% more information and other tutorials see the Million Song Website 
% http://labrosa.ee.columbia.edu/millionsong.
%
% This tutorial shows the basic access of the per-track data record 
% from within Matlab, and also shows how to use the provided SQLite 
% databases to search the metadata.

%% Setup
% 
% Before running this tutorial, you must complete the following 
% setup steps:
%
% (1) Obtain the Million Song Dataset, or Million Song Subset. 
% This demo is based on the Subset, but the commands are identical 
% for the full set.  You can download the Subset (2.8 GB) directly 
% from
% http://labrosa.ee.columbia.edu/millionsong/pages/getting-dataset .
% We assume this file has been decompressed to the directory 
% MillionSongSubset/ in the current directory (or modify code below).
%
% (2) Obtain the sample codebase.  You can download this from
% https://github.com/tb2332/MSongsDB .  We assume the entire tree
% has been decompressed into MSongsDB/ .
%
% (3) Obtain the Matlab SQLite interface mksqlite, available from 
% http://developer.berlios.de/projects/mksqlite/ .  We assume this 
% has been unpacked into mksqlite/ .
%
% Now we can make sure the SQLite interface is compiled, and the 
% paths are set up:

% Compile mksqlite (only needs to be done once)
cd mksqlite
buildit
cd ..
% add mksqlite to the path
addpath('mksqlite');

% set up Million Song paths
msd_subset_path='MillionSongSubset';  % or 'MillionSong' for full set?
msd_subset_data_path=[msd_subset_path,'/data'];
msd_subset_addf_path=[msd_subset_path,'/AdditionalFiles'];
msd_subset_addf_prefix=[msd_subset_addf_path,'/subset_']; % no 'subset_'?
% Check that we can actually read the dataset
assert(exist(msd_subset_path,'dir')==7,'msd_subset_path is wrong...');

% path to the Million Song Dataset code
msd_code_path='MSongsDB';
assert(exist(msd_code_path,'dir')==7,'msd_code_path is wrong...');
% add to the path
addpath([msd_code_path,'/MatlabSrc']);

%% Simple file access
%
% The Million Song Dataset stores the Echo Nest Analyze features
% and meta data for each track in its own HDF5 data file, organized
% into file hierarchy based on the Echo Nest hash codes.  First, we
% build a list of all h5 files under our data tree.  Then we load
% one file, look at the methods available, and plot the chroma for
% the first part of the file.  

% Build a list of all the files in the dataset
all_files = findAllFiles(msd_subset_data_path);
cnt = length(all_files);
disp(['Number of h5 files found: ',num2str(cnt)]);

% Get info from the first file using our wrapper
h5 = HDF5_Song_File_Reader(all_files{1});
disp(['artist name is: ',h5.get_artist_name()]);
disp([' song title is: ',h5.get_title()]);
% Show all the available methods
methods('HDF5_Song_File_Reader')
% .. covers all the EN Analyze API fields

% Plot the first 200 chromas
chromas = h5.get_segments_pitches();
subplot(311)
imagesc(chromas(:,1:200))
axis xy
colormap(1-gray)
colorbar
title('first 200 chromas');

%% Resynthesis
% 
% The EN Analyze features provide only a simplified description of
% the original audio; however, it's possible to reconstruct an 
% approximation of the original audio by combining the chroma, 
% timbre, and level features.  We've implemented a rough stab at 
% this.

% Resynthesize the first 30 seconds using chroma and timbre
% We need to set up the basis functions for the EN timbre dimensions
global ENTimbreBasis
load ENTimbreBasis
% Now can map features back to audio
sr = 16000;
dur = 30; % first 30s
x = synth_song(h5,dur,sr);
% Take a listen
soundsc(x,sr);
% recognizable?
% Plot the spectrogram, for comparison
subplot(312)
specgram(x,512,sr);
caxis(max(caxis)+[-80 0]);

%% Mapping over all the data files
%
% Many applications require searching over all the data files. 
% With a million tracks, this can take some time.  Even with the 
% subset (10,000 tracks, or 1% of the database), it takes a while:
% on a Macbook Pro, each HDF5 file access takes around 30ms, so 
% accessing 10,000 takes on the order of 5 minutes.  Here we do
% this, simply collecting the artist name for each track into 
% a cell array with 10,000 entries.

% Get all artist names by mapping a function to return artist names
% over the cell array of data file names
tic;
all_artist_names = cellfun(@(f) get_artist_name(HDF5_Song_File_Reader(f)), ...
                           all_files, 'UniformOutput', false);
tend = toc;
disp(['All names acquired in ',num2str(tend),' seconds.']);
disp(['First artist name is: ',all_artist_names{1}]);
disp(['There are ',num2str(length(unique(all_artist_names))), ...
      ' unique artist names']);
% takes around 5 min on MacBook Pro to scan 10k files (30ms/file)

%% SQLite Database Access
%
% Linear search over the files is evidently a painful process;
% extrapolating even the simple access above to 1M songs would take
% over 8 hours.  To avoid this for simple access of the metadata,
% we have pre-built SQLite databases containing the main metadata
% fields (Artist name, track name, release, MusicBrainz IDs, year
% of release, etc.).  These are conveniently accessed via the
% mksqlite function.
% 
% Let's try getting all the artist names again, using SQLite:

% Track metadata database
sqldb = [msd_subset_addf_prefix,'track_metadata.db'];
% Open connection
mksqlite('open',sqldb);
% Run the SQL query.  DISTINCT means we only get the unique names
artist_names = mksqlite('SELECT DISTINCT artist_name FROM songs');
% Close the connection (clean up)
mksqlite('close');
disp(['Found ',num2str(length(artist_names)),' distinct artist names']);
disp('First artist names are:');
for k=1:5;
    disp(artist_names(k).artist_name);
end

% Note that some artist have many artist names, usually when a song is
% 'featuring someone else'. Therefore, we should work with artist IDs.
% Find the artist ID (and name) for the artist with the most songs in
% the dataset.
mksqlite('open',sqldb);
res = mksqlite(['SELECT DISTINCT artist_id,artist_name,Count(track_id) ' ...
                'FROM songs GROUP BY artist_id']);
mksqlite('close');
disp('Got entries that looks like:');
res(1)

% Sort the results
[unused, order] = sort(arrayfun(@(x)getfield(x, ...
    'Count(track_id)'),res(:)),'descend');
res = res(order); 
disp('Artist with the most songs is:');
res(1)

% finally, get all songs for that artist
mksqlite('open',sqldb);
res = mksqlite(['SELECT track_id FROM songs WHERE artist_id='''...
                res(1).artist_id,'''']);
mksqlite('close');
disp(['Found ',num2str(length(res)),' tracks for that artist.']);
disp(['First one is: ',res(1).track_id]);


%% Acknowledgment
%
% This material is based in part upon work supported by the
% National Science Foundation under Grant No. IIS-0713334, by 
% Eastman Kodak Corp, and by the National Geospatial Intelligence 
% Agency NSERC program.  Any opinions, findings and conclusions or
% recomendations expressed in this material are those of the
% author(s) and do not necessarily reflect the views of the sponsors.
%
% Last updated: $Date: 2010/08/13 15:40:58 $
% Dan Ellis <dpwe@ee.columbia.edu>
% Thierry Bertin-Mahieux <tb2332@columbia.edu>
