function [urlConnection,errorid,errormsg] = urlreadwrite(fcn,urlChar)
%URLREADWRITE A helper function for URLREAD and URLWRITE.

%   Matthew J. Simoneau, June 2005
%   Copyright 1984-2005 The MathWorks, Inc.
%   $Revision: 1.1.6.1 $ $Date: 2005/06/21 19:35:35 $

% Default output arguments.
urlConnection = [];
errorid = '';
errormsg = '';

% Determine the protocol (before the ":").
protocol = urlChar(1:min(find(urlChar==':'))-1);

% Try to use the native handler, not the ice.* classes.
switch protocol
    case 'http'
        try
            handler = sun.net.www.protocol.http.Handler;
        catch
            handler = [];
        end
    case 'https'
        try
            handler = sun.net.www.protocol.https.Handler;
        catch
            handler = [];
        end
    otherwise
        handler = [];
end

% Create the URL object.
try
    if isempty(handler)
        url = java.net.URL(urlChar);
    else
        url = java.net.URL([],urlChar,handler);
    end
catch
    errorid = ['MATLAB:' fcn ':InvalidUrl'];
    errormsg = 'Either this URL could not be parsed or the protocol is not supported.';
    return
end

% Determine the proxy.
proxy = [];
if ~isempty(java.lang.System.getProperty('http.proxyHost'))
    try
        ps = java.net.ProxySelector.getDefault.select(java.net.URI(urlChar));
        if (ps.size > 0)
            proxy = ps.get(0);
        end
    catch
        proxy = [];
    end
end

% Open a connection to the URL.
if isempty(proxy)
    urlConnection = url.openConnection;
else
    urlConnection = url.openConnection(proxy);
end
