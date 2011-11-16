function [d,sr] = msd_load_preview(track_id, oauth_consumer_key)
% [d,sr] = msd_load_preview(track_id, oauth_consumer_key)
%    Load the 30s 7digital preview for a given track.
%    Requires you to provide your own 7digital API key, available at:
%    http://access.7digital.com/partnerprogram.
%    <track_id> is the EN track ID e.g. 'TRAAAAW128F429D538'
%    <oauth_consumer_key> is the 7digital ID e.g. 'abcde12345'
%    This routine downloads the 30 s preview available from 
%    7digital, then reads it into Matlab (using mp3read.m) to 
%    return a regular waveform (stereo, 44 kHz).
% 2011-01-30  Dan Ellis dpwe@ee.columbia.edu

% Get the id7 ID
id7digital = get_track_7digitalid(HDF5_Song_File_Reader(msd_pathname(track_id)));

% Download from 7digital
[status, result] = system(['wget ''http://api.7digital.com/1.2/track/preview?trackid=',num2str(id7digital),'&oauth_consumer_key=',oauth_consumer_key,'''']);

if status ~= 0
  error(['Error downloading preview:',result]);
end

% figure out what file name it was saved as
bb = max(strfind(result, 'Saving to:'));

if length(bb) == 0
  error(['Unable to identify name of downloaded file in: ', ...
         result]);
end

ofs = 12;  % chars between start of 'Saving to:' and beginning of filename
ee = min([strfind(result((bb+ofs):end),'"'),strfind(result((bb+ofs):end),'''')]);
fname = result((bb+ofs):(bb+ofs+ee-2));

if exist(fname,'file') ~= 2
  error(['Allegedly download file "',fname,'" not found']);
else
  % read in that mp3 file
  [d,sr] = mp3read(fname);

  % clean up
  system(['rm ',fname]);
end

