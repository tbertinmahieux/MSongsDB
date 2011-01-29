function Y = chrompeaks(X,N)
% Y = chrompeaks(X,N)
%   X is a 12xN chroma feature matrix.  Find local maxima in each 
%   column (i.e. the peaks) and set all other values to zero, 
%   return in Y.  This would be useful prior to resynthesis.
%   Optional N limits each column to N nonzero values max.
% 2007-11-10 dpwe@ee.columbia.edu

if nargin < 2
  N = size(X,1);
end


% Wrap around edge rows
[nr,nc] = size(X);
Xm = (X > X([2:nr,1],:)) & (X >= X([nr,1:nr-1],:));
Y = Xm.*X;

[VV,XX] = sort(-Y);

% find indices of bottom rows
XX = repmat(nr*[0:(nc-1)],nr,1)+XX;
XXX = XX((N+1):end,:);

% Make sure all those values are zero
Y(XXX(:)) = 0;
