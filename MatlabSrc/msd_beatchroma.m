function [C,Tbeats,Tsegs] = msd_beatchroma(id, nbeats)
% C = msd_beatchroma(id)
%   Return beat-synchronous chroma features derived from 
%   the MSD Echo Nest analyze features.  Segs is the 12xN 
%   array of chroma features from EN Analyze, and Tsegs
%   is the vector of segment times.  Tbeats is a vector 
%   of beat times; the segments overlapping each beat 
%   interval are averaged and returned in C.
%   Alternatively, pass in the entire EN Analyze structure as 
%   returned by en_analyze.m to read the data from there.
% 2010-04-08 Dan Ellis dpwe@ee.columbia.edu
%
% Added by TBM
% nbeats  - align every nbeats, default=1

nchr = 12;

if nargin < 2
    nbeats = 1;
end

if isstruct(id)
  ENAstruct = id;
else
  ENAstruct = en_analyze_msd(id);
end

% read chroma out of structure; apply per-segment loudness
Segs = ENAstruct.pitches .* repmat(10.^(ENAstruct.segmentloudness/ ...
                                        20),nchr,1);

% read times too
Tsegs = ENAstruct.segment;
Tbeats = ENAstruct.beat(1:nbeats:end);

%%%% Old way
%  Tres = 0.01;
%  % We do this the quick and dirty way by upsampling to Tres 
%  % resolution, then averaging down again
%
%  % Set duration as one segment beyond the last beat time
%  duration = 2*Tbeats(end) - Tbeats(end-1);
%
%  % Y = samplemx(D.pitches*diag(idB(D.segmentloudness)./sqrt(sum(D.pitches))),D.segmentstart, [0:0.01:D.duration]);
%  SegsUpsamp = samplemx(Segs, Tsegs, 0:Tres:duration);
%
%  % then downsample down again
%  C = beatavg(SegsUpsamp, Tbeats/Tres);

% Now properly figure time overlaps & weight
C = resample_mx(Segs, Tsegs, Tbeats);
% and renormalize columns
n = max(C);
C = C.*repmat(1./n,size(C,1),1);
