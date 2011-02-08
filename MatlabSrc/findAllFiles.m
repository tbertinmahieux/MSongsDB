function fileList = findAllFiles(dirName,ext)
% fileList = findAllFiles(dirName,ext)
%   returns a cell array containing the file names of all files
%   ending in <ext> (default: '.h5') below directory <dirName>.
%
% THIS IS MODIFIED FROM THIS BLOG POST:
% http://stackoverflow.com/questions/2652630/how-to-get-all-files-under-
% a-specific-directory-in-matlab
% THIS IS MATLAB DONE BY SOMEONE THAT DOES NOT LIKE MATLAB ;)
% We welcome any sort of improvement! -TBM
%
% 2011-01-27 dpwe@ee.columbia.edu tb2332@columbia.edu

if (nargin < 2); % default extension: .h5
  ext = '.h5';
end

dirData = dir(dirName);      % Get the data for the current directory
dirIndex = [dirData.isdir];  % Find the index for directories
fileListTmp = {dirData(~dirIndex).name}';  %'# Get a list of the files
fileList = {};
% keep files with the right extension
for k=1:size(fileListTmp,1)
  [d,n,e] = fileparts(cell2mat(fileListTmp(k)));
  if strcmp(e,ext)
    fileList = cat(1,fileList,fileListTmp(k));
  end
end
if ~isempty(fileList)
  fileList = cellfun(@(x) fullfile(dirName,x),... % Prepend path to files
                     fileList,'UniformOutput',false);
end

% cnt
cnt = size(fileList,1);

subDirs = {dirData(dirIndex).name};  % Get a list of the subdirectories
validIndex = ~ismember(subDirs,{'.','..'});  % Find index of subdirs
                                             %  that are not '.' or '..'
% Loop over valid subdirectories
for iDir = find(validIndex)             
  % Get the subdirectory path
  % Recursively call findAllFiles
  sublist = findAllFiles([dirName,'/',subDirs{iDir}],ext);
  fileList = [fileList;sublist];
  cnt = cnt + length(sublist);
end






