function E = recons_env_h5(A)
% E = recons_env_h5(A)
%    Reconstruct the time-frequency envelope of a sound from the EN
%    timbre descriptors.  A is a EN HDF5_Song structure including
%    segment start times and segment durations.  Reconstruct 
%    each segment envelope from the A.timbre coefficient weights, 
%    resample it, insert it into E.
% 2010-05-03 Dan Ellis dpwe@ee.columbia.edu

global ENTimbreTJ

if length(ENTimbreTJ) == 0
  [p,n,e] = fileparts(which('recons_env_h5'));
  load(fullfile(p,'ENTimbreTJ.mat'));
end

segments = A.get_segments_start()';
segmentduration = diff(segments);
%maxtime = A.get_duration();
% just clone the last known duration
segmentduration = [segmentduration, segmentduration(end)];
timbre = A.get_segments_timbre();

bases = ENTimbreTJ.bases;
bmean = ENTimbreTJ.mean;

% pass off to the unified subsidiary function
E = recons_env_sub(segments, segmentduration, timbre, bases, bmean);
