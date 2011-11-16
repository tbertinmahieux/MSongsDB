function E = recons_env(A)
% E = recons_env(A)
%    Reconstruct the time-frequency envelope of a sound from the EN
%    timbre descriptors, using Tristan Jehan's coefficients and
%    instructions.  
%    A is a EN analysis structure including 
%    A.segment start times and A.segmentduration durations.  B is a
%    matrix of N x M x 12 envelope basis functions.  Reconstruct 
%    each segment envelope from the A.timbre coefficient weights, 
%    resample it, insert it into E.
% 2010-05-03 Dan Ellis dpwe@ee.columbia.edu

global ENTimbreTJ

if length(ENTimbreTJ) == 0
  [p,n,e] = fileparts(which('recons_env'));
  load(fullfile(p,'ENTimbreTJ.mat'));
end

segments = A.segment;
segmentduration = A.segmentduration;
timbre = A.timbre;

bases = ENTimbreTJ.bases;
bmean = ENTimbreTJ.mean;

E = recons_env_sub(segments, segmentduration, timbre, bases, bmean);
