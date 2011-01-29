function E = recons_env_h5(A,B)
% E = recons_env_h5(A,B)
%    Reconstruct the time-frequency envelope of a sound from the EN
%    timbre descriptors.  A is a EN HDF5_Song structure including
%    segment start times and segment durations.  B is a
%    matrix of N x M x 12 envelope basis functions.  Reconstruct 
%    each segment envelope from the A.timbre coefficient weights, 
%    resample it, insert it into E.
% 2010-05-03 Dan Ellis dpwe@ee.columbia.edu

global ENTimbreBasis

if nargin < 2
  if length(ENTimbreBasis)==0
    load ENTimbreBasis
  end
  B = ENTimbreBasis;
end

segments = A.get_segments_start()';
segmentduration = diff(segments);
nseg = length(segments);
%maxtime = A.get_duration();
% just clone the last known duration
segmentduration = [segmentduration, segmentduration(end)];
maxtime = segments(end)+segmentduration(end);

nchan = size(B,1);
ncol = size(B,2);
ntimb = size(B,3);

tbase = 0.010;
E = zeros(nchan,ceil(maxtime/tbase)+1);
tt = tbase * [0:(ceil(maxtime/tbase))];

timbre = A.get_segments_timbre();

for s = 1:nseg
  ei = zeros(nchan,ncol);
  for i = 1:ntimb
    ei = ei + squeeze(timbre(i,s)*B(:,:,i));
  end
  ei2 = [ei,ei(:,end)];
  % Figure out the actual place to put it
  % Segment covers A.segment(s) to
  % A.segment(s)+A.segmentduration(s) in ncol steps
  % thus each col k of ei corresponds to time 
  % A.segment(s)+k*A.segmentduration(s)/ncol
  tk = segments(s)+[0:(ncol-1)]/ncol*segmentduration(s);
  trix = find(tt >= tk(1), 1, 'first'):(find(tt<=tk(end), 1, 'last')+1);
                                        
  tk2 = [tk tk(end)+1];
  trp = zeros(1,length(trix));
  for j = 1:length(trix);
    trp(j) = find(tk<=tt(trix(j)), 1,'last');
    trp(j) = trp(j) + (tt(trix(j))-tk(trp(j)))/(tk2(trp(j)+1)-tk(trp(j)));
  end
%  E(:,trix) = E(:,trix) + idB(A.segmentloudness(s))*(colinterp(ei2,trp).^(1/0.3));
  E(:,trix) = E(:,trix) + (colinterp(ei2,trp).^(1/0.3));
end
