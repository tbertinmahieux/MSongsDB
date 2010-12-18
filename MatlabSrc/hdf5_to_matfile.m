% Thierry Bertin-Mahieux (2010) Columbia University
% tb2332@columbia.edu
%
% This code contains a set of routines to convert an HDF5 song file
% from the Million Song Dataset project to a matfile.
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


function hdf5_to_matfile(hdf5path,matpath)
% This code contains a set of routines to convert an HDF5 song file
% from the Million Song Dataset project to a matfile.
% INPUT:
%    hdf5path  - path a to HDF5 song file
%    matpath   - desired path for the new mafile (OPTIONAL)
%                default: hdf5path with extension replaced by .mat
% Note: developped with Matlab 2009b

    % assert hdf5 file exists
    if exist(hdf5path,'file') ~= 2
        disp(strcat('hdf5 file ',hdf5path,' does not exists.'));
        return;
    end
    % check matfile path (creates it if necessary)
    if nargin < 2
        [pathstr, name, ext] = fileparts(hdf5path);
        matpath = fullfile(pathstr,strcat(name,'.mat'));
    end
    if exist(matpath,'file') == 2
        disp(strcat('matfile ',matpath,' exists, please delete or change mat path'));
        return;
    end
    % open HDF5
    h5 = HDF5_Song_File_Reader(hdf5path);
    % num songs
    nSongs = h5.get_num_songs();
    % get all members, keep the getters (remove get_num_songs)
    h5methods = methods(h5);
    idx = cellfun(@(x) strcmp(x(1:4),'get_'),h5methods);
    getters = {h5methods{idx}};
    idx = cellfun(@(x) ~strcmp(x,'get_num_songs'),getters);
    getters = {getters{idx}};
    % iterate over songs inside file
    transfer_note = strcat('transferred on ',datestr(now),' from file: ',hdf5path,' using MATLAB');
    save(matpath, 'transfer_note','-v7');
    for songidx = 1:nSongs
        for getidx = 1:size(getters,2)
            % new matfile field name
            gettername = getters{getidx}(5:end);
            if nSongs > 1
                gettername = strcat(gettername,num2str(songidx));
            end
            % get value
            eval(strcat(gettername,' = h5.',getters{getidx},'(',num2str(songidx),');'));
            % write value to matfile
            save(matpath, gettername, '-append','-v7');
        end % end iteration over getters
    end % end iteration over songs
    
    
    
    
    