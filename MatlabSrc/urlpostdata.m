%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
function [output,status] = urlpostdata(urlChar,params,data)
%URLPOST Sends binary data via HTTP POST and returns result
%   S = URLPOSTDATA('URL',PARAMS,DATA) passes information to the server as
%   a POST request.  PARAMS is a cell array of param/value pairs,
%   which are encoded onto the end of the URL.
%   
%   Unlike stock urlread, this version takes DATA as a binary data
%   record (represented as UINT8), and appends it to the POST as 
%   Content-Type:application/octet-stream
%
%   f = fopen('music.mp3');
%   d = fread(f,Inf,'*uint8');  % Read in byte stream of MP3 file
%   fclose(f);
%   s =
%   urlpostdata('http://developer.echonest.com/api/v4/track/upload', ...
%     {'api_key',API_KEY,'filetype','mp3'}, ...
%     d);
%
%   ... will upload the mp3 file to the Echo Nest Analyze service version 4.
%
%  Based on TMW's URLREAD.  Note that unlike URLREAD, there is no
%  METHOD argument
% 2011-11-15 Dan Ellis dpwe@ee.columbia.edu


% POST /api/v4/track/upload?api_key=N6E4NIOVYMTHNDM8J&filetype=mp3 HTTP/1.1
% User-Agent: curl/7.21.6 (x86_64-apple-darwin10.7.0) libcurl/7.21.6 OpenSSL/1.0.0d zlib/1.2.5 libidn/1.22
% Host: developer.echonest.com
% Accept: */*
% Content-Type:application/octet-stream
% Content-Length: 37476
% Expect: 100-continue


%  2010-04-07 Dan Ellis dpwe@ee.columbia.edu

% This function requires Java.
if ~usejava('jvm')
   error('MATLAB:urlreadpost:NoJvm','URLREADPOST requires Java.');
end

import com.mathworks.mlwidgets.io.InterruptibleStreamCopier;

% Be sure the proxy settings are set.
com.mathworks.mlwidgets.html.HTMLPrefs.setProxySettings

% Set default outputs.
output = '';
status = 0;

% build query string
qstr = '';
for i = 1:2:length(params)
  if i == 1
    qstr = [qstr,'?'];
  else
    qstr = [qstr,'&'];
  end
  qstr = [qstr,params{i},'=',params{i+1}];
end

urlChar = [urlChar,qstr];
%disp(urlChar);

% Create a urlConnection.
[urlConnection,errorid,errormsg] = urlreadwrite(mfilename,urlChar);
if isempty(urlConnection)
  error(errorid,errormsg);
end

% write out the binary data too, preceded by a header
urlConnection.setDoOutput(true);
urlConnection.setRequestProperty('Content-Type','application/octet-stream');
printStream = java.io.PrintStream(urlConnection.getOutputStream);
% also create a binary stream
dataOutputStream = java.io.DataOutputStream(urlConnection.getOutputStream);
eol = [char(13),char(10)];

% binary data is uploaded as an octet stream
printStream.print(['Content-Type: application/octet-stream',eol]);
printStream.print(['Content-Length: ',num2str(length(data)),eol]);
printStream.print(['Expect: 100-continue',eol]);
printStream.print([eol]);

dataOutputStream.write(data,0,length(data));
printStream.print([eol]);
printStream.close;

% Read the data from the connection.
try
    inputStream = urlConnection.getInputStream;
    byteArrayOutputStream = java.io.ByteArrayOutputStream;
    % This StreamCopier is unsupported and may change at any time.
    isc = InterruptibleStreamCopier.getInterruptibleStreamCopier;
    isc.copyStream(inputStream,byteArrayOutputStream);
    inputStream.close;
    byteArrayOutputStream.close;
    output = native2unicode(typecast(byteArrayOutputStream.toByteArray','uint8'),'UTF-8');
catch
    if catchErrors, return
    else error('MATLAB:urlreadpost:ConnectionFailed','Error downloading URL. Your network connection may be down or your proxy settings improperly configured.');
    end
end

status = 1;
