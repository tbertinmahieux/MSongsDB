function E = en_recons_env(A)
% E = en_recons_env(A)
%    Reconstruct the time-frequency envelope of a sound from the EN
%    timbre descriptors.  A is either an EN HDF5_Song object, or an
%    EN analyze structure from en_analyze[_msd], which includes
%    segment start times and segment durations.  Reconstruct 
%    each segment envelope from the A.timbre coefficient weights, 
%    resample it, insert it into E.
% 2010-05-03 Dan Ellis dpwe@ee.columbia.edu

global ENTimbreTJ

if length(ENTimbreTJ) == 0
  [p,n,e] = fileparts(which('en_recons_env_h5'));
  load(fullfile(p,'ENTimbreTJ.mat'));
end

if isstruct(A)
  % struct means an en_analyze structure
  segments = A.segment;
  segmentduration = A.segmentduration;
  timbre = A.timbre;
else
  % else assume an h5 object, or the name of an MSD item
  if ischar(A)
    % load the MSD file
    A = HDF5_Song_File_Reader(msd_pathname(A));
  end
  % get info from h5 object
  segments = A.get_segments_start()';
  segmentduration = diff(segments);
  %maxtime = A.get_duration();
  % just clone the last known duration
  segmentduration = [segmentduration, segmentduration(end)];
  timbre = A.get_segments_timbre();
end

bases = ENTimbreTJ.bases;
bmean = ENTimbreTJ.mean;

nseg = length(segments);
maxtime = segments(end) + segmentduration(end);

nchan = size(bases,1);
ncols = size(bases,2);
ntimb = size(bases,3);

%tbase = 0.010;
tbase = 128/22050;
E = zeros(nchan,ceil(maxtime/tbase)+1);
tt = tbase * [0:(ceil(maxtime/tbase))];

% How many uninterpolated frames
ninitial = 10;
% How many subsequent interpolated frames
nfinal = ncols - ninitial;

for s = 1:nseg
  % reconstruction starts with mean + constant value of 1st element
  ei = bmean + timbre(1,s);
  for i = 1:ntimb
    ei = ei + squeeze(timbre(i+1,s)*bases(:,:,i));
  end
  ei2 = [ei,ei(:,end)];
  % First 10 frames are unresampled
  % next 10 frames are linearly interpolated for the remainder
  tk = segments(s) + [0:(ninitial-1)]*tbase;
  tk = [tk, segments(s)+ninitial*tbase ...
        + [1:(nfinal)]/nfinal*(segmentduration(s)-ninitial*tbase)];
%  plot(tk,'.');
%  title(['segment ', num2str(s)]);
%  pause
  trix = find(tt >= tk(1), 1, 'first'):(find(tt<=tk(end), 1, 'last')+1);
                                        
  tk2 = [tk tk(end)+1];
  goodtrix = (trix <= size(E,2));
  trix = trix(goodtrix);
  trp = zeros(1,length(trix));
  for j = 1:length(trix);
    trp(j) = find(tk<=tt(trix(j)), 1,'last');
    trp(j) = trp(j) + (tt(trix(j))-tk(trp(j)))/(tk2(trp(j)+1)-tk(trp(j)));
  end
%  E(:,trix) = E(:,trix) +
%  idB(A.segmentloudness(s))*(colinterp(ei2,trp).^(1/0.3));
%  E(:,trix) = E(:,trix) + (colinterp(ei2,trp));
  % just overwrite any overlap
%  E(:,trix) = 10.^(colinterp(ei2,trp)/20);
  E(:,trix) = colinterp(ei2,trp);
end
