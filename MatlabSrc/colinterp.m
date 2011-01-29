function c = colinterp(b, t)
% c = colinterp(b, t)   Interpolate columns in a matrix
%     b is a specgram-style matrix
%     t is a vector of (real) time-samples, which specifies a path through 
%     the time-base defined by the columns of b.  For each value of t, 
%     the magnitudes in the columns of b are interpolated, 
%     a new column is created in the output array c.
%     Note: t is defined relative to a zero origin, so 0.1 is 90% of 
%     the first column of b, plus 10% of the second.
% 2009-01-27 dpwe@ee.columbia.edu  cut down version of pvsample.m
% $Header: /homes/dpwe/public_html/resources/matlab/RCS/pvsample.m,v 1.2 2002/02/13 16:15:27 dpwe Exp $

[rows,cols] = size(b);

% Empty output array
c = zeros(rows, length(t));

% Append a 'safety' column on to the end of b to avoid problems 
% taking *exactly* the last frame (i.e. 1*b(:,cols)+0*b(:,cols+1))
b = [b,zeros(rows,1)];

ocol = 1;
for tt = t
  % Grab the two columns of b
  bcols = b(:,floor(tt)+[1 2]);
  tf = tt - floor(tt);
  bmag = (1-tf)*abs(bcols(:,1)) + tf*(abs(bcols(:,2)));
  % Save the column
  c(:,ocol) = bmag;
  ocol = ocol+1;
end
