function x = synth_song(M,dur,sr,donoise)
% x = synth_song(M,dur,sr,donoise)
%    Resynthesize audio from an EN analyze structure.
%    M is an HDF_Song_File_Reader structure
%    x is returned as a waveform synthesized from that data, with
%    max duration <dur> secs (duration of song), at sampling rate
%    sr (16000 Hz).  donoise = 1 => noise excited.
%    (based on echonest/play_en.m)
%    Now with EN-provided resynthesis parameters.
% 2011-11-13, 2009-03-11 Dan Ellis dpwe@ee.columbia.edu

if nargin < 2; dur = 0; end
if nargin < 3; sr = 22050; end
if nargin < 4; donoise = 0; end

% include denormalization by loudness
C = M.get_segments_pitches(); % .* repmat(idB(M.segmentloudness),nchr,1);
% denormalization now in timbre reconstruction
[nchr, nbeats] = size(C);

beattimes = M.get_segments_start()';

if dur > 0
  nbeats = sum(beattimes <= dur);
  beattimes = beattimes(1:nbeats);
  C = C(:,1:nbeats);
end

dowt = 0;
maxnpitch = 6;

%x = synthesize_chroma(C,beattimes,sr);
x = chromsynth2(C,beattimes,sr,0,maxnpitch);

%%%%% PUT ENVELOPE RECONSTRUCTION FROM TIMBRE FEATURES IN HERE %%%%%%

EdB = recons_env_h5(M);
% E returns in (pseudo?) dB; convert to linear
E = 10.^(EdB/20);

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
DE = diag(1./SM)*M'*E;
if size(DE,2) < size(X,2)
  DE(1,size(X,2)) = DE(1,end);
end

x = ispecgram(X.*DE(:,1:size(X,2)), fftlen, sr, winlen, winlen-hoplen);

if nargout == 0
  soundsc(x,sr);
end
