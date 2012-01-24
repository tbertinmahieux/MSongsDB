function T = en_song2track(song_id, API_KEY, verbose)
% T = en_song2track(song_id, API_KEY, verbose)
%    Use Echonest API to convert a SongID (e.g. from Taste Profile) 
%    to a track ID (that can be looked up in MSD).
% 2011-12-21 Dan Ellis dpwe@ee.columbia.edu

if nargin < 2
  API_KEY = '';
end

if nargin < 3
  verbose = 0;
end

if length(API_KEY) == 0
  % try environment variable
  API_KEY = getenv('EN_API_KEY');
  if length(API_KEY) == 0
	API_KEY='XXXXXXXXXXXXXXXXX';  % get a key from
                                  % http://developer.echonest.com/
  end                              
end

% read back the entire analysis structure
%str = urlread('http://developer.echonest.com/api/v4/song/profile', 'get', ...
%                  {'api_key',API_KEY,'format','json', ...
%                   'id', song_id, ...
%	         	   'bucket','tracks'});
url = ['http://developer.echonest.com/api/v4/song/profile?' ...
               'api_key=',API_KEY,'&format=','json', ...
               '&id=', song_id, ...
               '&bucket=','id:7digital-US','&bucket=','tracks'];
disp(url);
str = urlread(url);
ddisp('got profile response', verbose);

% find the full analysis structure
ret = p_json(str);

%T = ret;
assert(length(ret.response.songs)==1);

T = ret.response.songs{1};

ddisp('done', verbose);


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
function ddisp(s,v)
if(v) 
  disp(s)
end
