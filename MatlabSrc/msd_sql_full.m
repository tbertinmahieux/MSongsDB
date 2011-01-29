function res = msd_sql_full(q)
mksqlite('open','MillionSong/AdditionalFiles/track_metadata.db');
res = mksqlite(q);
mksqlite('close');
disp(['returned ',num2str(length(res)),' results']);
