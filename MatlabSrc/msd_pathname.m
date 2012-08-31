function n = msd_pathname(f)
% convert a track ID into an H5 filename
%n = ['MillionSongSubset/data/',f(3),'/',f(4),'/',f(5),'/',f,'.h5'];

global MillionSong

n = [MillionSong,'/data/',f(3),'/',f(4),'/',f(5),'/',f,'.h5'];

