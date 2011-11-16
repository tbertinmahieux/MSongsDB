function M = en_mfcc(A)
% M = en_mfcc(A)
%   Take a data structure A containing EN Analyze features (as
%   returned by en_analyze or en_analyze_msd) or an h5 object or an
%   MSD trakc ID, and convert it into MFCCs (similar to the return 
%   from melfcc).
%   M is 20 rows, with one column for every 5.8ms frame recovered
%   from the original data (128 samples at 22,050 Hz sample rate).
%   This approximates:
%      melfcc(d/100, sr, 'wintime', 0.032, 'hoptime', 128/22050,
%             'minfreq',133.33,'maxfreq',6855.6,'numcep',20,'lifterexp',0);
%
% 2011-11-16 Dan Ellis dpwe@ee.columbia.edu

% Reconstruct the Bark-scale envelope
env = en_recons_env(A);
% E returns in (pseudo?) dB; convert to linear (60 dB alignment)
env = 10.^((env-100.0)/20);
% convert to melfcc-scale
env = env*32768*4;

nfft = 512;
nbark = size(env,1);
sr = 22050;
% Mel filter / MFCC params - copy Slaney's mfcc.m
minfreq = 133.33;
maxfreq = 6855.6;
bwidth = 1.0;
nbands = 40;
numcep = 20;
dcttype = 2;
lifterexp = 0;

% Construct Bark -> FFT matrix
b2f = inline_fft2jbarkmx(nfft, sr, nbark, 1.0);
% normalize
b2f = b2f(:,1:(nfft/2+1));
SM = sum(b2f);
% b2f flattened along FFT bin frequencies
b2f = b2f*diag(1./SM);
SMP = sum(b2f.^2,2);
% b2f equalized for the output power
%b2f = diag(1./sqrt(SMP))*b2f;
% transpose to make it map barks to fft
b2f = b2f';

% FFT -> mel matrix
f2m = inline_fft2melmx(nfft, sr, nbands, bwidth, minfreq, maxfreq);
f2m = f2m(:,1:(nfft/2+1));

% Mel spectra
% (weighting in linear amplitude domain, result as power spectrum)
melspec = ((f2m*b2f)*env).^2;

% MFCCs
M = inline_lifter(inline_spec2cep(melspec, numcep, dcttype), lifterexp);

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% from rastamat
function [cep,dctm] = inline_spec2cep(spec, ncep, type)
% [cep,dctm] = spec2cep(spec, ncep, type)
%     Calculate cepstra from spectral samples (in columns of spec)
%     Return ncep cepstral rows (defaults to 9)
%     This one does type II dct, or type I if type is specified as 1
%     dctm returns the DCT matrix that spec was multiplied by to give cep.
% 2005-04-19 dpwe@ee.columbia.edu  for mfcc_dpwe

if nargin < 2;   ncep = 13;   end
if nargin < 3;   type = 2;   end   % type of DCT

[nrow, ncol] = size(spec);

% Make the DCT matrix
dctm = zeros(ncep, nrow);
if type == 2 || type == 3
  % this is the orthogonal one, the one you want
  for i = 1:ncep
    dctm(i,:) = cos((i-1)*[1:2:(2*nrow-1)]/(2*nrow)*pi) * sqrt(2/nrow);
  end
  if type == 2
    % make it unitary! (but not for HTK type 3)
    dctm(1,:) = dctm(1,:)/sqrt(2);
  end
elseif type == 4 % type 1 with implicit repeating of first, last bins
  % Deep in the heart of the rasta/feacalc code, there is the logic 
  % that the first and last auditory bands extend beyond the edge of 
  % the actual spectra, and they are thus copied from their neighbors.
  % Normally, we just ignore those bands and take the 19 in the middle, 
  % but when feacalc calculates mfccs, it actually takes the cepstrum 
  % over the spectrum *including* the repeated bins at each end.
  % Here, we simulate 'repeating' the bins and an nrow+2-length 
  % spectrum by adding in extra DCT weight to the first and last
  % bins.
  for i = 1:ncep
    dctm(i,:) = cos((i-1)*[1:nrow]/(nrow+1)*pi) * 2;
    % Add in edge points at ends (includes fixup scale)
    dctm(i,1) = dctm(i,1) + 1;
    dctm(i,nrow) = dctm(i,nrow) + ((-1)^(i-1));
  end
  dctm = dctm / (2*(nrow+1));
else % dpwe type 1 - same as old spec2cep that expanded & used fft
  for i = 1:ncep
    dctm(i,:) = cos((i-1)*[0:(nrow-1)]/(nrow-1)*pi) * 2 / (2*(nrow-1));
  end
  % fixup 'non-repeated' points
  dctm(:,[1 nrow]) = dctm(:, [1 nrow])/2;
end  

cep = dctm*log(spec);
  

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% from rastamat
function y = inline_lifter(x, lift, invs)
% y = lifter(x, lift, invs)
%   Apply lifter to matrix of cepstra (one per column)
%   lift = exponent of x i^n liftering
%   or, as a negative integer, the length of HTK-style sin-curve liftering.
%   If inverse == 1 (default 0), undo the liftering.
% 2005-05-19 dpwe@ee.columbia.edu

if nargin < 2;   lift = 0.6; end   % liftering exponent
if nargin < 3;   invs = 0; end      % flag to undo liftering

[ncep, nfrm] = size(x);

if lift == 0
  y = x;
else

  if lift > 0
    if lift > 10
      disp(['Unlikely lift exponent of ', num2str(lift),' (did you mean -ve?)']);
    end
    liftwts = [1, ([1:(ncep-1)].^lift)];
  elseif lift < 0
    % Hack to support HTK liftering
    L = -lift;
    if (L ~= round(L)) 
      disp(['HTK liftering value ', num2str(L),' must be integer']);
    end
    liftwts = [1, (1+L/2*sin([1:(ncep-1)]*pi/L))];
  end

  if (invs)
    liftwts = 1./liftwts;
  end

  y = diag(liftwts)*x;

end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% from rastamat
function [wts,binfrqs] = inline_fft2melmx(nfft, sr, nfilts, width, minfrq, maxfrq, htkmel, constamp)
% [wts,frqs] = fft2melmx(nfft, sr, nfilts, width, minfrq, maxfrq, htkmel, constamp)
%      Generate a matrix of weights to combine FFT bins into Mel
%      bins.  nfft defines the source FFT size at sampling rate sr.
%      Optional nfilts specifies the number of output bands required 
%      (else one per "mel/width"), and width is the constant width of each 
%      band relative to standard Mel (default 1).
%      While wts has nfft columns, the second half are all zero. 
%      Hence, Mel spectrum is fft2melmx(nfft,sr)*abs(fft(xincols,nfft));
%      minfrq is the frequency (in Hz) of the lowest band edge;
%      default is 0, but 133.33 is a common standard (to skip LF).
%      maxfrq is frequency in Hz of upper edge; default sr/2.
%      You can exactly duplicate the mel matrix in Slaney's mfcc.m
%      as fft2melmx(512, 8000, 40, 1, 133.33, 6855.5, 0);
%      htkmel=1 means use HTK's version of the mel curve, not Slaney's.
%      constamp=1 means make integration windows peak at 1, not sum to 1.
%      frqs returns bin center frqs.
% 2004-09-05  dpwe@ee.columbia.edu  based on fft2barkmx

if nargin < 2;     sr = 8000;      end
if nargin < 3;     nfilts = 0;     end
if nargin < 4;     width = 1.0;    end
if nargin < 5;     minfrq = 0;     end  % default bottom edge at 0
if nargin < 6;     maxfrq = sr/2;  end  % default top edge at nyquist
if nargin < 7;     htkmel = 0;     end
if nargin < 8;     constamp = 0;   end

if nfilts == 0
  nfilts = ceil(inline_hz2mel(maxfrq, htkmel)/2);
end

wts = zeros(nfilts, nfft);

% Center freqs of each FFT bin
fftfrqs = [0:(nfft/2)]/nfft*sr;

% 'Center freqs' of mel bands - uniformly spaced between limits
minmel = inline_hz2mel(minfrq, htkmel);
maxmel = inline_hz2mel(maxfrq, htkmel);
binfrqs = inline_mel2hz(minmel+[0:(nfilts+1)]/(nfilts+1)*(maxmel-minmel), htkmel);

binbin = round(binfrqs/sr*(nfft-1));

for i = 1:nfilts
%  fs = inline_mel2hz(i + [-1 0 1], htkmel);
  fs = binfrqs(i+[0 1 2]);
  % scale by width
  fs = fs(2)+width*(fs - fs(2));
  % lower and upper slopes for all bins
  loslope = (fftfrqs - fs(1))/(fs(2) - fs(1));
  hislope = (fs(3) - fftfrqs)/(fs(3) - fs(2));
  % .. then intersect them with each other and zero
%  wts(i,:) = 2/(fs(3)-fs(1))*max(0,min(loslope, hislope));
  wts(i,1+[0:(nfft/2)]) = max(0,min(loslope, hislope));

  % actual algo and weighting in feacalc (more or less)
%  wts(i,:) = 0;
%  ww = binbin(i+2)-binbin(i);
%  usl = binbin(i+1)-binbin(i);
%  wts(i,1+binbin(i)+[1:usl]) = 2/ww * [1:usl]/usl;
%  dsl = binbin(i+2)-binbin(i+1);
%  wts(i,1+binbin(i+1)+[1:(dsl-1)]) = 2/ww * [(dsl-1):-1:1]/dsl;
% need to disable weighting below if you use this one

end

if (constamp == 0)
  % Slaney-style mel is scaled to be approx constant E per channel
  wts = diag(2./(binfrqs(2+[1:nfilts])-binfrqs(1:nfilts)))*wts;
end

% Make sure 2nd half of FFT is zero
wts(:,(nfft/2+2):nfft) = 0;
% seems like a good idea to avoid aliasing


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
function f = inline_mel2hz(z, htk)
%   f = mel2hz(z, htk)
%   Convert 'mel scale' frequencies into Hz
%   Optional htk = 1 means use the HTK formula
%   else use the formula from Slaney's mfcc.m
% 2005-04-19 dpwe@ee.columbia.edu

if nargin < 2
  htk = 0;
end

if htk == 1
  f = 700*(10.^(z/2595)-1);
else
  
  f_0 = 0; % 133.33333;
  f_sp = 200/3; % 66.66667;
  brkfrq = 1000;
  brkpt  = (brkfrq - f_0)/f_sp;  % starting mel value for log region
  logstep = exp(log(6.4)/27); % the magic 1.0711703 which is the ratio needed to get from 1000 Hz to 6400 Hz in 27 steps, and is *almost* the ratio between 1000 Hz and the preceding linear filter center at 933.33333 Hz (actually 1000/933.33333 = 1.07142857142857 and  exp(log(6.4)/27) = 1.07117028749447)

  linpts = (z < brkpt);

  f = 0*z;

  % fill in parts separately
  f(linpts) = f_0 + f_sp*z(linpts);
  f(~linpts) = brkfrq*exp(log(logstep)*(z(~linpts)-brkpt));

end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
function z = inline_hz2mel(f,htk)
%  z = hz2mel(f,htk)
%  Convert frequencies f (in Hz) to mel 'scale'.
%  Optional htk = 1 uses the mel axis defined in the HTKBook
%  otherwise use Slaney's formula
% 2005-04-19 dpwe@ee.columbia.edu

if nargin < 2
  htk = 0;
end

if htk == 1
  z = 2595 * log10(1+f/700);
else
  % Mel fn to match Slaney's Auditory Toolbox mfcc.m

  f_0 = 0; % 133.33333;
  f_sp = 200/3; % 66.66667;
  brkfrq = 1000;
  brkpt  = (brkfrq - f_0)/f_sp;  % starting mel value for log region
  logstep = exp(log(6.4)/27); % the magic 1.0711703 which is the ratio needed to get from 1000 Hz to 6400 Hz in 27 steps, and is *almost* the ratio between 1000 Hz and the preceding linear filter center at 933.33333 Hz (actually 1000/933.33333 = 1.07142857142857 and  exp(log(6.4)/27) = 1.07117028749447)

  linpts = (f < brkfrq);

  z = 0*f;

  % fill in parts separately
  z(linpts) = (f(linpts) - f_0)/f_sp;
  z(~linpts) = brkpt+(log(f(~linpts)/brkfrq))./log(logstep);

end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% from nearby
function wts = inline_fft2jbarkmx(nfft, sr, nfilts, width, minfreq, maxfreq)
% wts = fft2jbarkmx(nfft, sr, nfilts, width, minfreq, maxfreq)
%      Generate a matrix of weights to combine FFT bins into Bark
%      bins using Jehan mapping.  nfft defines the source FFT size at sampling rate sr.
%      Optional nfilts specifies the number of output bands required 
%      (else one per bark), and width is the constant width of each 
%      band in Bark (default 1).
%      While wts has nfft columns, the second half are all zero. 
%      Hence, Bark spectrum is fft2bjarkmx(nfft,sr)*abs(fft(xincols,nfft));
% 2004-09-05  dpwe@ee.columbia.edu  based on rastamat/audspec.m

if nargin < 3;    nfilts = 0;     end
if nargin < 4;    width = 1.0;    end
if nargin < 5;    minfreq = 0;    end
if nargin < 6;    maxfreq = sr/2; end

min_bark = inline_hz2jbark(minfreq);
nyqbark = inline_hz2jbark(maxfreq) - min_bark;
if nfilts == 0
  nfilts = ceil(nyqbark)+1;
end

wts = zeros(nfilts, nfft);

% bark per filt
step_barks = nyqbark/(nfilts-1);

% Frequency of each FFT bin in Bark
binbarks = inline_hz2jbark([0:nfft/2]*sr/nfft);

for i = 1:nfilts
  f_bark_mid = min_bark + (i-1) * step_barks;
  % Linear slopes in log-space (i.e. dB) intersect to trapezoidal window
  lof = (binbarks - f_bark_mid - 0.5);
  hif = (binbarks - f_bark_mid + 0.5);
  wts(i,1:(nfft/2+1)) = 10.^(min(0, min([hif; -2.5*lof])/width));
end

function z = inline_hz2jbark(f)
% z = hz2jbark(f)
%
% map frequency in hz to bark using the same formula as Jehan.
%
% Dan Ellis dpwe@ee.columbia.edu 2011-11-12

% eqn. 3.3, p.45 of Jehan05-phd.pdf

z = 13 * atan(0.00076*f) + 3.5*atan((f/7500).^2);

