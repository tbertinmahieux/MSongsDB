function x = chromsynth2(F,bp,sr,dowt,npks)
% x = chromsynth2(F,bp,sr,dowt,npks)
%   Resynthesize a chroma feature vector to audio
%   F is 12 rows x some number of columns, one per beat
%   bp is the period of one beat in sec (or a vector of beat times)
%   sr is the sampling rate of the output waveform
%   x is returned as a 12 semitone-spaced sines modulated by F
%   Actual Shepard tones now implemented! 2007-04-19
%   If dowt is 0, don't weight the sines, but just leave them flat
%   npks is the maximum number of peaks to retain in each chroma
%   frame.  Default is all of them.
% 2006-07-14 dpwe@ee.columbia.edu

if nargin < 2; bp = 0.5; end % 120 bpm
if nargin < 3; sr = 22050; end
if nargin < 4; dowt = 1; end
if nargin < 5; npks = 0; end

[nchr,nbts] = size(F);

% maybe prune peaks
if npks > 0
  F = chrompeaks(F,npks);
end

% get actual times
if length(bp) == 1
  bts = bp*[0:size(F,2)];
else
  bts = bp;
end
if length(bts) < (nbts+1)   % +1 to have end time of final note
  medbt = median(diff(bts));
  bts = [bts, bts(end)+medbt*[1:((nbts+1)-length(bts))]];
end

% crossfade overlap time
dt = 0.01;
dtsamp = round(dt*sr);

% Generate 12 basic shepard tones
dur = max(diff(bts)); % max duration
dursamp = round(dur*sr);
nchr = 12;
octs = 10;
basefrq = 27.5*(2^(3/12));  % A1+3 semis = C2;

tones = zeros(nchr, dursamp + 2*dtsamp + 1);
tt = [0:(size(tones,2)-1)]/sr;

% what bin is the center freq?
f_ctr = 440;
f_sd = 0.5;
f_bins = basefrq*2.^([0:(nchr*octs - 1)]/nchr);
f_dist = log(f_bins/f_ctr)/log(2)/f_sd;  
% Gaussian weighting centered of f_ctr, with f_sd
if (dowt)
  f_wts = exp(-0.5*f_dist.^2);
else
  % flat weights
  f_wts = ones(1,length(f_dist));
end
% Sum up sinusoids
for i = 1:nchr
  for j = 1:octs
    bin = nchr*(j-1) + i;
    if f_bins(bin) < sr/2
      omega = 2* pi * f_bins(bin);
      tones(i,:) = tones(i,:)+f_wts(bin)*sin(omega*tt);
    end
  end
end

% resynth
x = zeros(1,round(max(bts)*sr));

ee = round(sr * bts(1));
for b = 1:size(F,2);
  ss = ee+1;
  ee = round(sr * bts(b+1));
  twin = 0.5*(1-cos([0:dtsamp-1]/(dtsamp-1)*pi));
  twin = [twin,ones(1,ee-ss+1),fliplr(twin)];
  sss = ss - dtsamp;
  eee = ee + dtsamp;
  if eee > length(x)
    twin = twin(1:end-(eee-length(x)));
    eee = length(x);
  end
  if sss < 1
    twin = twin((2-sss):end);
    sss = 1;
  end
  
  ll = 1+eee-sss;
  dd = zeros(1,ll);
  for i = 1:nchr
    if F(i,b)>0
      dd = dd + F(i,b)*tones(i,1:ll);
    end
  end
  x(sss:eee) = x(sss:eee) + twin .* dd;
  
end

