function x = en_resynth(A,dur,sr,donoise)
% x = en_resynth(A,dur,sr,donoise)
%    Resynthesize audio from an EN analyze structure.
%    A is an HDF_Song_File_Reader structure or MSD ID or en_analyze output
%    x is returned as a waveform synthesized from that data, with
%    max duration <dur> secs (duration of song), at sampling rate
%    sr (16000 Hz).  donoise = 1 => noise excited.
%    (based on echonest/play_en.m)
%    Now with EN-provided resynthesis parameters.
% 2011-11-13, 2009-03-11 Dan Ellis dpwe@ee.columbia.edu

if nargin < 2; dur = 0; end
if nargin < 3; sr = 22050; end
if nargin < 4; donoise = 0; end

if isstruct(A)
  % struct means an en_analyze structure
  C = A.pitches;
  beattimes = [0,cumsum(A.segmentduration)];
else
  % else assume an h5 object
  if ischar(A)
    % load the MSD file
    A = HDF5_Song_File_Reader(msd_pathname(A));
  end
  % get info from h5 object
  C = A.get_segments_pitches();
  beattimes = A.get_segments_start()';
end

[nchr, nbeats] = size(C);

if dur > 0
  nbeats = sum(beattimes <= dur);
  beattimes = beattimes(1:nbeats);
  C = C(:,1:nbeats);
end

dowt = 0;
maxnpitch = 6;

%x = synthesize_chroma(C,beattimes,sr);
x = chromsynth2(C,beattimes,sr,0,maxnpitch);

EdB = en_recons_env(A);
% E returns in (pseudo?) dB; convert to linear (60 dB alignment)
E = 10.^((EdB-60.0)/20);

%hoplen = round(sr*.010);
%winlen = round(sr*.025);
hoplen = round(sr * 128/22050);
winlen = round(2.5*hoplen);
fftlen = 2^ceil(log(winlen)/log(2));

if donoise
  X = specgram(randn(1,length(x)),fftlen,sr,winlen,winlen-hoplen);
else
  X = specgram(x,fftlen,sr,winlen,winlen-hoplen);
end
%X = specgram(randn(1,length(x)),fftlen,sr,winlen,winlen-hoplen);
M = fft2jbarkmx(fftlen,sr,size(E,1),1.0);
M = M(:,1:(fftlen/2+1));
SM = sum(M);
% M flattened along FFT bin frequencies
M = M*diag(1./SM);
SMP = sum(M.^2,2);
% M equalized for the output power
M = diag(1./(SMP))*M;
% Now reconstruct into FFT space
DE = M'*E;
if size(DE,2) < size(X,2)
  DE(1,size(X,2)) = DE(1,end);
end

x = ispecgram(X.*DE(:,1:size(X,2)), fftlen, sr, winlen, winlen-hoplen);

if nargout == 0
  soundsc(x,sr);
end
