function res = msd_sql(q)

global MillionSong MSDsubset

mksqlite('open',[MillionSong,'/AdditionalFiles/',MSDsubset,'track_metadata.db']);
res = mksqlite(q);
mksqlite('close');
disp(['returned ',num2str(length(res)),' results']);
