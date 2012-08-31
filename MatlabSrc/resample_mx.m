function Y = resample_mx(X, incolpos, outcolpos)
% Y = resample_mx(X, incolpos, outcolpos)
%    X is taken as a set of columns, each starting at "time"
%    colpos, and continuing until the start of the next column.  
%    Y is a similar matrix, with time boundaries defined by 
%    outcolpos.  Each column of Y is a duration-weighted average of
%    the overlapping columns of X.
% 2010-04-14 Dan Ellis dpwe@ee.columbia.edu  based on samplemx/beatavg

noutcols = length(outcolpos);
Y = zeros(size(X,1),noutcols);

% assign "end times" to final columns
if max(outcolpos) > max(incolpos)
  incolpos = [incolpos,max(outcolpos)];
  X = [X,X(:,end)];
end
outcolpos = [outcolpos,outcolpos(end)];

% durations (default weights) of input columns)
incoldurs = [diff(incolpos),1];

for c = 1:noutcols
  firstincol = find(incolpos <= outcolpos(c), 1, 'last');
  lastincol = max(firstincol,find(incolpos < outcolpos(c+1), 1, ...
                                  'last'));
%  disp(sprintf('firstincol=%d lastincol=%d',firstincol,lastincol));
  % default weights
  wts = incoldurs(firstincol:lastincol);
  % now fix up by partial overlap at ends
  if length(wts) > 1
    wts(1) = wts(1) - (outcolpos(c) - incolpos(firstincol));
    wts(end) = wts(end) - (incolpos(lastincol+1) - outcolpos(c+1));
  end
  wts = wts/sum(wts);
  Y(:,c) = X(:,firstincol:lastincol)*wts';
end
