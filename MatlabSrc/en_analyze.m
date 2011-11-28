function D = en_analyze(F, verbose)
% D = en_analyze(F, verbose)
%     Pass an MP3 file whose filename is F to the Echo Nest
%     Analyze API, and return the analyzed data.
%     If F is a "music:TR..." key, skip upload and query that track.
%     F can also be the bytes of an MP3 file (if of type uint8).
%
%     This version uses Analyze v4 and json format for data return.
%     It relies on p_json.m .
% 2011-04-11 Dan Ellis dpwe@ee.columbia.edu

API_KEY='XXXXXXXXXXXXXXXXX';  % get a key from http://developer.echonest.com/

if nargin < 2
  verbose = 0;
end

if isnumeric(F) || strncmp(F, 'music:', 6)==0

  if isa(F,'uint8')
    % F is the bytes read from an mp3 file
    d = F;
  else
    if isnumeric(F)
      % maybe accept a waveform - but then we'd need a sampling
      % rate.  We'd have to mp3write it to a temporary file, then
      % upload that.
      error('F was numeric but not bytes - unrecognized type');
    end
    % We were passed an actual file name
    % Read in the MP3 file
    f = fopen(F);
    d = fread(f,Inf,'*uint8');  % Read in byte stream of MP3 file
    fclose(f);
  end

  ddisp('uploading mp3', verbose);

  % Post to EN Analyze
  % readpost with single argument posts an octet-stream, as
  % required for v4; rest of args go into URL
  str = urlpostdata('http://developer.echonest.com/api/v4/track/upload', ...
                    {'api_key',API_KEY,'filetype','mp3', ...
                     'wait','true','format','json'}, ...
                    d);

  ddisp('upload complete', verbose);

  % Grab return
  ret = p_json(str);

  % Check EN fields
  retcode = ret.response.status.code;
  if retcode ~= 0  % ret.status.code
   disp(['******* upload returned ', num2str(retcode), 
         ' - ',ret.response.status.message]);
   D = [];
   return
  end

  % Get track ID
  track = ret.response.track.id;
  % always report track ID
else
  if strncmp(F, 'music:', 6)
    F = F(7:end);
    if max(F=='/') > 0
      F = F(max(find(F=='/'))+1:end);
    end
  end
  track = F;
end
  
disp(['track ID=',track]);
D.id = track;

% read back the entire analysis structure
str = urlreadpost('http://developer.echonest.com/api/v4/track/analyze', ...
                  {'api_key',API_KEY,'format','json','id',track, ...
                   'bucket','audio_summary','wait','true'});
ddisp('got analyze response', verbose);

% find the full analysis structure
ret = p_json(str);

trackinfo = ret.response.track;

analysis_url = trackinfo.audio_summary.analysis_url;
str = urlread(analysis_url);
ddisp('got analysis url data', verbose);

analysis = p_json(str);
ddisp('parsed analysis url data', verbose);

nsegs = length(analysis.segments);
nchr = length(analysis.segments{1}.pitches);
ntimb = length(analysis.segments{1}.timbre);

D.pitches = zeros(nchr, nsegs);
D.timbre = zeros(ntimb, nsegs);
D.segment = zeros(1, nsegs);
D.segmentduration = zeros(1, nsegs);
D.segmentloudness = zeros(1, nsegs);
D.segmentloudnessmax = zeros(1, nsegs);
D.segmentloudnessmaxtime = zeros(1, nsegs);

%Trial>> str2num(analysis(5).sub(2).sub(3).sub(1).data)
% 3rd chroma coef of 5th frame

for i = 1:nsegs
  D.pitches(:,i) = cellfun(@(x) x, analysis.segments{i}.pitches)';
  D.timbre(:,i) = cellfun(@(x) x, analysis.segments{i}.timbre)';
%  D.segment(i) = d.analysis.segment(i).ATTRIBUTE.start;  % D.segment or D.segmentstart?
%  D.segmentduration(i) = d.analysis.segment(i).ATTRIBUTE.duration;
%  D.segmentloudness(i) = d.analysis.segment(i).loudness.dB(1).CONTENT;
%  D.segmentloudnessmax(i) = d.analysis.segment(i).loudness.dB(2).CONTENT;
%  D.segmentloudnessmaxtime(i) = d.analysis.segment(i).loudness.dB(2).ATTRIBUTE.time;
end

D.segment = cellfun(@(x) x.start, analysis.segments);
D.segmentduration = cellfun(@(x) x.duration, analysis.segments);
D.segmentloudness = cellfun(@(x) x.loudness_start, analysis.segments);
D.segmentloudnessmax = cellfun(@(x) x.loudness_max, analysis.segments);
D.segmentloudnessmaxtime = cellfun(@(x) x.loudness_max_time, analysis.segments);

ddisp('segment info parsed', verbose);

% Read the tatums
%ntatums = length(d.analysis.tatum);
ntatums = length(analysis.tatums);
D.tatum = cellfun(@(x) x.start, analysis.tatums);
D.tatumconfidence = cellfun(@(x) x.confidence, analysis.tatums);

% Read the beats
nbeats = length(analysis.beats);
D.beat = cellfun(@(x) x.start, analysis.beats);
D.beatconfidence = cellfun(@(x) x.confidence, analysis.beats);

ddisp('beat info parsed', verbose);

% Read the bars
nbars = length(analysis.bars);
D.bar = cellfun(@(x) x.start, analysis.bars);
D.barconfidence = cellfun(@(x) x.confidence, analysis.bars);

ddisp('bar info parsed', verbose);

% Read the sections
nsections = length(analysis.sections);
D.section = cellfun(@(x) x.start, analysis.sections);
D.sectionduration = cellfun(@(x) x.duration, analysis.sections);
D.sectionconfidence = cellfun(@(x) x.confidence, analysis.sections);

ddisp(' parsing remaining fields', verbose);

% Single value attributes
D.end_of_fade_in = analysis.track.end_of_fade_in;
D.start_of_fade_out = analysis.track.start_of_fade_out;
D.key = analysis.track.key;
D.keyconfidence = analysis.track.key_confidence;
D.mode = analysis.track.mode;
D.modeconfidence = analysis.track.mode_confidence;
D.loudness = analysis.track.loudness;
D.tempo = analysis.track.tempo;
D.tempoconfidence = analysis.track.tempo_confidence;
D.time_signature = analysis.track.time_signature;
D.time_signatureconfidence = analysis.track.time_signature_confidence;

% Metadata
% Set whatever we get, but ensure artist, release, and title exist
D.artist = '';
D.release = '';
D.title = '';

metafield = fieldnames(trackinfo);
for i = 1:length(metafield)
  field = metafield{i};
  val = getfield(trackinfo,field);
  if ~isstruct(val)
    D = setfield(D,field,val);
  end
end
% and for audio_summary fields
metafield = fieldnames(trackinfo.audio_summary);
for i = 1:length(metafield)
  field = metafield{i};
  val = getfield(trackinfo.audio_summary,field);
  if ~isstruct(val)
    D = setfield(D,field,val);
  end
end

ddisp('done', verbose);


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
function ddisp(s,v)
if(v) 
  disp(s)
end
