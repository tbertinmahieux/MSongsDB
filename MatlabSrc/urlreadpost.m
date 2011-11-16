%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
function [output,status] = urlreadpost(urlChar,params)
%URLREADPOST Returns the contents of a URL POST method as a string.
%   S = URLREADPOST('URL',PARAMS) passes information to the server as
%   a POST request.  PARAMS is a cell array of param/value pairs.
%   
%   Unlike stock urlread, this version uses the multipart/form-data
%   encoding, and can thus post file content.  File data is 
%   encoded as a value element of numerical type (e.g. uint8)
%   in PARAMS.  For example:
%
%   f = fopen('music.mp3');
%   d = fread(f,Inf,'*uint8');  % Read in byte stream of MP3 file
%   fclose(f);
%   str = urlreadpost('http://developer.echonest.com/api/upload', ...
%           {'file',dd,'version','3','api_key','API-KEY','wait','Y'});
%
%   ... will upload the mp3 file to the Echo Nest Analyze service.
%
%  Based on TMW's URLREAD.  Note that unlike URLREAD, there is no
%  METHOD argument

%  2010-04-07 Dan Ellis dpwe@ee.columbia.edu

% This function requires Java.
if ~usejava('jvm')
   error('MATLAB:urlreadpost:NoJvm','URLREADPOST requires Java.');
end

import com.mathworks.mlwidgets.io.InterruptibleStreamCopier;

% Be sure the proxy settings are set.
com.mathworks.mlwidgets.html.HTMLPrefs.setProxySettings

% Check number of inputs and outputs.
error(nargchk(2,2,nargin))
error(nargoutchk(0,2,nargout))
if ~ischar(urlChar)
    error('MATLAB:urlreadpost:InvalidInput','The first input, the URL, must be a character array.');
end

% Do we want to throw errors or catch them?
if nargout == 2
    catchErrors = true;
else
    catchErrors = false;
end

% Set default outputs.
output = '';
status = 0;

% Create a urlConnection.
[urlConnection,errorid,errormsg] = urlreadwrite(mfilename,urlChar);
if isempty(urlConnection)
    if catchErrors, return
    else error(errorid,errormsg);
    end
end

% POST method.  Write param/values to server.
% Modified for multipart/form-data 2010-04-06 dpwe@ee.columbia.edu
%    try
        urlConnection.setDoOutput(true);
        boundary = '***********************';
        urlConnection.setRequestProperty( ...
            'Content-Type',['multipart/form-data; boundary=',boundary]);
        printStream = java.io.PrintStream(urlConnection.getOutputStream);
        % also create a binary stream
        dataOutputStream = java.io.DataOutputStream(urlConnection.getOutputStream);
        eol = [char(13),char(10)];
        for i=1:2:length(params)
          printStream.print(['--',boundary,eol]);
          printStream.print(['Content-Disposition: form-data; name="',params{i},'"']);
          if ~ischar(params{i+1})
            % binary data is uploaded as an octet stream
            % Echo Nest API demands a filename in this case
            printStream.print(['; filename="dummy"',eol]);
            % ?
            printStream.print(['Content-Type: application/octet-stream',eol]);
            printStream.print([eol]);
            dataOutputStream.write(params{i+1},0,length(params{i+1}));
            printStream.print([eol]);
          else
            printStream.print([eol]);
            printStream.print([eol]);
            printStream.print([params{i+1},eol]);
          end
        end
        printStream.print(['--',boundary,'--',eol]);
        printStream.close;
%    catch
%        if catchErrors, return
%        else error('MATLAB:urlread:ConnectionFailed','Could not POST to URL.');
%        end
%    end

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
