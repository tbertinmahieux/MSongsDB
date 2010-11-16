% Thierry Bertin-Mahieux (2010) Columbia University
% tb2332@columbia.edu
%
% This code contains a set of routines to create HDF5 files containing
% features and metadata of a song.
%
% This is part of the Million Song Dataset project from
% LabROSA (Columbia University) and The Echo Nest.
%
% Copyright 2010, Thierry Bertin-Mahieux
%
% This program is free software: you can redistribute it and/or modify
% it under the terms of the GNU General Public License as published by
% the Free Software Foundation, either version 3 of the License, or
% (at your option) any later version.
%
% This program is distributed in the hope that it will be useful,
% but WITHOUT ANY WARRANTY; without even the implied warranty of
% MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
% GNU General Public License for more details.
%
% You should have received a copy of the GNU General Public License
% along with this program.  If not, see <http://www.gnu.org/licenses/>.
%


classdef HDF5_Song_File_Reader
% Class to read a song HDF5 file form the Million Song Dataset Project
% The class caches data as it is requested, i.e. class can take lots of
% memory at the end.
% Any question / comment: tb2332@columbia.edu

    % PROPERTIES, we cache all requested information + handles
    properties (SetAccess = public) % after debugging, should be private
        h5filename='';   % stores the filename to the HDF5 object
        h5fileID=0;      % stores the handle to the HDF5 object
        % datasets ID
        analysisID=0;    % handle for /analysis/songs
        metadataID=0;    % handle for /metadata/songs
        % data
        analysis
        metadata
    end
    
    % METHODS: constructor, destructor, getters
    methods
        
      function obj = HDF5_Song_File_Reader(h5filename)
      % Constructor, receives a filename
         obj.h5filename=h5filename;
         obj.h5fileID=H5F.open(h5filename,'H5F_ACC_RDONLY','H5P_DEFAULT');
         obj.metadataID = H5D.open(obj.h5fileID,'/metadata/songs');
         obj.metadata = H5D.read(obj.metadataID, 'H5ML_DEFAULT', 'H5S_ALL', 'H5S_ALL', 'H5P_DEFAULT');
         obj.analysisID = H5D.open(obj.h5fileID,'/analysis/songs');
         obj.analysis = H5D.read(obj.analysisID, 'H5ML_DEFAULT', 'H5S_ALL', 'H5S_ALL', 'H5P_DEFAULT');
      end % topo
      
      function delete(obj)
      % destructor, closes h5 file
        % these data ID are always open
        H5D.close(obj.analysisID);
        H5D.close(obj.metadataID);
        % close the fileID
        H5F.close(obj.h5fileID);
      end
      
      %*********************************************************
      % GETTERS
      % songidx always 1 by default
      
      function res = get_num_songs(obj)
      % number of songs contained in the HDF5 file, usually 1,
      % unless it is a 'summary' file.
        res = size(obj.metadata.duration,1);
      end
      
      function res = get_artist_familiarity(obj,songidx)
        if nargin < 2
            songidx = 1;
        end
        res = obj.metadata.artist_familiarity(songidx);
      end
      
      function res = get_artist_hotttnesss(obj,songidx)
        if nargin < 2
            songidx = 1;
        end  
        res = obj.metadata.artist_hotttnesss(songidx);
      end
      
      function res = get_artist_id(obj,songidx)
        if nargin < 2
            songidx = 1;
        end  
        res = obj.metadata.artist_id(:,songidx);
      end
      
      function res = get_artist_latitude(obj,songidx)
        if nargin < 2
            songidx = 1;
        end  
        res = obj.metadata.artist_latitude(songidx);
      end
      
      function res = get_artist_longitude(obj,songidx)
        if nargin < 2
            songidx = 1;
        end  
        res = obj.metadata.artist_longitude(songidx);
      end
      
      function res = get_artist_location(obj,songidx)
        if nargin < 2
            songidx = 1;
        end  
        res = obj.metadata.artist_location(:,songidx);
      end
      
      function res = get_artist_name(obj,songidx)
        if nargin < 2
            songidx = 1;
        end  
        res = obj.metadata.artist_name(:,songidx);
      end
      
      function res = get_song_hotttnesss(obj,songidx)
        if nargin < 2
            songidx = 1;
        end  
        res = obj.metadata.song_hotttnesss(songidx);
      end
      
      function res = get_title(obj,songidx)
        if nargin < 2
            songidx = 1;
        end  
        res = obj.metadata.title(:,songidx);
      end
      
      function res = get_beats_start(obj,songidx)
      % return beats start for a given song (starting at 1)
          if nargin < 2
              songidx = 1;
          end
          data = hdf5read(obj.h5filename,'/analysis/beats_start');
          pos1 = obj.analysis.idx_beats_start(songidx)+1;
          if songidx == obj.get_num_songs()  
            res = data(pos1:end);
          else
            pos2 = obj.analysis.idx_beats_start(songidx+1); % +1 -1
            res = data(pos1:pos2);
          end
      end
      
      % END GETTERS
      
    end % END METHODS
    
end % END CLASS