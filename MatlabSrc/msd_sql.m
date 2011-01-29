function res = msd_sql(q)
mksqlite('open','MillionSongSubset/AdditionalFiles/subset_track_metadata.db');
res = mksqlite(q);
mksqlite('close');
disp(['returned ',num2str(length(res)),' results']);
