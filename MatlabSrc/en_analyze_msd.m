function D = en_analyze_msd(F, verbose)
% D = en_analyze_msd(F, verbose)
%     Return the Echo Nest Analyze fields for a particular track.  
%     This version uses the Million Song Dataset records, but
%     returns a structure that matches the result from en_analyze.m 
%     (which actually passes an mp3 file to the EN API).
% 2011-04-12 Dan Ellis dpwe@ee.columbia.edu

if nargin < 2
  verbose = 0;
end

if strncmp(F, 'music:', 6)
  F = F(7:end);
end

if strncmp(F, 'TR', 2) == 0
  error('en_analyze_msd only accepts a TR... identifier')
end

track = F;

%disp(['track ID=',track]);
D.id = track;

% Read the MSD file
MSD = HDF5_Song_File_Reader(msd_pathname(track));

D.pitches = get_segments_pitches(MSD);
D.timbre = get_segments_timbre(MSD);
D.segment = get_segments_start(MSD)';
D.segmentduration = max(0,diff([D.segment, get_start_of_fade_out(MSD)]));
D.segmentloudness = get_segments_loudness_start(MSD)';
D.segmentloudnessmax = get_segments_loudness_max(MSD)';
D.segmentloudnessmaxtime = get_segments_loudness_max_time(MSD)';

D.tatum = get_tatums_start(MSD)';
D.tatumconfidence = get_tatums_confidence(MSD)';

D.beat = get_beats_start(MSD)';
D.beatconfidence = get_beats_confidence(MSD)';

D.bar = get_bars_start(MSD)';
D.barconfidence = get_bars_confidence(MSD)';

D.section = get_sections_start(MSD)';
D.sectionconfidence = get_sections_confidence(MSD)';
D.sectionduration = max(0,diff([D.section, get_start_of_fade_out(MSD)]));

% Single value attributes
D.end_of_fade_in = get_end_of_fade_in(MSD);
D.start_of_fade_out = get_start_of_fade_out(MSD);
D.key = get_key(MSD);
D.keyconfidence = get_key_confidence(MSD);
D.mode = get_mode(MSD);
D.modeconfidence = get_mode_confidence(MSD);
D.loudness = get_loudness(MSD);
D.tempo = get_tempo(MSD);
%D.tempoconfidence = get_tempo_confidence(MSD);
% tempo confidence is not in MSD files
D.tempoconfidence = -1;  % impossible value
D.time_signature = get_time_signature(MSD);
D.time_signatureconfidence = get_time_signature_confidence(MSD);

% Metadata
% Set whatever we get, but ensure artist, release, and title exist
D.artist = get_artist_name(MSD);
D.release = get_release(MSD);
D.title = get_title(MSD);
D.duration = get_duration(MSD);
D.sample_rate = get_analysis_sample_rate(MSD);
D.audio_md5 = get_audio_md5(MSD);
D.energy = get_energy(MSD);
D.danceability = get_danceability(MSD);
% MSD-specific
D.track_7digitalid = get_track_7digitalid(MSD);
D.artist_familiarity = get_artist_familiarity(MSD);
D.year = get_year(MSD);

ddisp('done', verbose);


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
function ddisp(s,v)
if(v) 
  disp(s)
end




