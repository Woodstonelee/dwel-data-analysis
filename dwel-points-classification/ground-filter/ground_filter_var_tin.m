function ground_filter_var_tin(dwel_pts_file, out_dir, varargin)
% Take a DWEL point cloud ASCII file and filter points with
% varying-scale TIN method.
%
% Syntax
%
%    ground_filter_var_tin(dwel_pts_file, out_dir, Name, Value) 
% 
% Options for Name/Value pairs
% 
%    scale, nx1 vector
%
%    door, nx1 vector
% 
%    refine_ground, boolean
%
%    max_range, scalar
% 
%    deltaz, scalar

%----------------------------------
% Iputs needed to be set beforehand
% dwel_pts_file, input DWEL point cloud ASCII file name.
% out_dir, directory for the filtering outputs.

% max_range and deltaz is to refine the ground point extraction at
% the end by fitting a plane to points within max_range and remove
% points with vertical distances to the plane larger than deltaz. 
options = struct('scale', [4.0000; 2.0000; 1.0000; 0.5000], ...
                 'door', [3.0000; 1.5000; 0.5000; 0.2000], ...
                 'refine_ground', false, ...
                 'max_range', 10, ...
                 'deltaz', 0.25);

option_names = fieldnames(options);

nargs = length(varargin);
if round(nargs/2) ~= nargs/2
   error('ground_filter_var_tin options need option_name / option_value pairs!');
end

for pairs = reshape(varargin, 2, [])
    inp_name = lower(pairs{1});
    if any(strcmp(inp_name, option_names))
       options.(inp_name) = pairs{2};
    else
        error('%s is not a recognized option name', inp_name);
    end
end

scale = options.scale;
door = options.door;
refine_ground = options.refine_ground;
max_range = options.max_range;
deltaz = options.deltaz;

% end of inputs
% -------------

dwel_ncol=19;
dwel_skip_header=3;
dwel_delimiter=',';

[fp1, fp2, fp3] = fileparts(dwel_pts_file);
ScanPtsPathName=fp1;
ScanPtsFileName=[fp2, fp3];
InPtsPathName=out_dir;
InPtsFileName=[fp2, '_refmt4gfvt', fp3];

fprintf('ScanPtsPathName to be processed: %s\n', ScanPtsPathName);
fprintf('ScanPtsFileName to be processed: %s\n', ScanPtsFileName);
fprintf('Temporary InPtsPathName for the following processing: %s\n', InPtsPathName);
fprintf('Temporary InPtsFileName for the following processing: %s\n', InPtsFileName);

fprintf('Loading and reformatting point cloud data ... \n');

fid = fopen(fullfile(ScanPtsPathName, ScanPtsFileName));
data = textscan(fid, repmat('%f', 1, dwel_ncol), 'HeaderLines', dwel_skip_header, 'Delimiter', dwel_delimiter);
fclose(fid);
data = cell2mat(data);
x = data(:, 1);
y = data(:, 2);
z = data(:, 3);
num_returns = data(:, 7);
% class = data(:, 24);
clear data;

line_num = (1:length(x))';

% remove zero-hit points
tmpflag = num_returns > 0;
x = x(tmpflag);
y = y(tmpflag);
z = z(tmpflag);
% class = class(tmpflag);
line_num = line_num(tmpflag);

fid = fopen(fullfile(InPtsPathName, InPtsFileName), 'w');
fprintf(fid, '%f\t%f\t%f\n', ([x, y, z])');
fclose(fid);

% output the line number of points in the original input point cloud.
fid = fopen(fullfile(InPtsPathName, [InPtsFileName, '.lnum']), 'w');
fprintf(fid, '%d\n', line_num);
fclose(fid);

fprintf('Reformatting points ASCII file finished!\n');

% files to output filtered ground points:
GroundPtsPathName = out_dir;
GroundPtsFileName = [fp2, '_ground_xyz', fp3];

fprintf('Output GroundPtsPathName: %s\n', GroundPtsPathName);
fprintf('Output GroundPtsFileName: %s\n', GroundPtsFileName);

fprintf('Filtering ground with varying-scale TIN ...\n');

xlim(1) = min(x);
xlim(2) = max(x);
ylim(1) = min(y);
ylim(2) = max(y);

extent = [xlim(1), xlim(2), ylim(1), ylim(2)];
fprintf('XoY bounding box of the point cloud to be filtered: \nminx\tmaxx\tminy\tmaxy\n%.3f\t%.3f\t%.3f\t%.3f\n', ...
        extent');

NewCutH = mexFilterVarScaleTIN(InPtsPathName, InPtsFileName, ...
                  GroundPtsPathName, GroundPtsFileName, ...
                  scale, door, ...
                  xlim, ylim, ...
                  nan(1,1), [0.2, 4], ...
                  [], [], []); 
clear functions;

fid = fopen(fullfile(GroundPtsPathName, [GroundPtsFileName, '.lnum']));
line_num = textscan(fid, '%d');
fclose(fid);
line_num = cell2mat(line_num);

if refine_ground
    fprintf('Refine ground points by fitting a plane\n');

    gpfid=fopen(fullfile(GroundPtsPathName, GroundPtsFileName), 'r');
    rawdata=textscan(gpfid,'%f %f %f');
    fclose(gpfid);
    datax=rawdata{1};
    datay=rawdata{2};
    dataz=rawdata{3};
    clear rawdata;
    [B, P, newind] = ransacfitplane(([datax, datay, dataz])', 1, 0);

    newgpfid=fopen(fullfile(GroundPtsPathName, GroundPtsFileName), 'w');
    fprintf(newgpfid, '%.3f %.3f %.3f\n', ([datax(newind), datay(newind), dataz(newind)])');
    fclose(newgpfid);

    fid = fopen(fullfile(GroundPtsPathName, [GroundPtsFileName, '.lnum']), 'w');
    fprintf(fid, '%d\n', line_num(newind));
    fclose(fid);
    line_num = line_num(newind);
end

% delete the InPtsFile, the input point clouds file that is simply
% reformated from the orginal DWEL points file
delete(fullfile(InPtsPathName, InPtsFileName));
delete(fullfile(InPtsPathName, [InPtsFileName, '.lnum']));

fprintf('Extracting/labeling ground points from/to original input DWEL point clouds\n');

% files to output filtered ground points in original DWEL formats:
ground_dwel_pts_file = fullfile(out_dir, [fp2, '_ground', fp3]);
labeled_dwel_pts_file = fullfile(out_dir, [fp2, '_gf', fp3]); % point cloud with ground labels

fprintf('Output of extracted ground points from DWEL point cloud: %s\n', ground_dwel_pts_file);
fprintf('Output of labeled ground points to DWEL point cloud: %s\n', labeled_dwel_pts_file);

fid = fopen(fullfile(ScanPtsPathName, ScanPtsFileName));
header = textscan(fid, '%s', dwel_skip_header, 'Delimiter', '\n');
fclose(fid);
fid = fopen(fullfile(ScanPtsPathName, ScanPtsFileName));
data = textscan(fid, '%s', 'HeaderLines', dwel_skip_header, 'Delimiter', '\n');
fclose(fid);
fid = fopen(ground_dwel_pts_file, 'w');
nfid = fopen(labeled_dwel_pts_file, 'w');
for i=1:length(header{1})
    fprintf(fid, '%s\n', header{1}{i});
    if i==1
        fprintf(nfid, '%s,ground_label\n', header{1}{i});
    else
        fprintf(nfid, '%s\n', header{1}{i});
    end
end
ground_flag = zeros(length(data{1}), 1);
ground_flag(line_num) = 1;
ground_flag = logical(ground_flag);
nrows = length(data{1});
progress_cnt = round(0.1*nrows);
fprintf('Writing progress percentage: 0');
for i=1:nrows
    if ground_flag(i)
        fprintf(fid, '%s\n', data{1}{i});
        fprintf(nfid, '%s,1\n', data{1}{i});
    else
        fprintf(nfid, '%s,0\n', data{1}{i});
    end
    if mod(i, progress_cnt) == 0
       fprintf('...%.0f', 100*i/nrows);
    end
end
fprintf('\n');
fclose(fid);
fclose(nfid);

fprintf('Ground filtering by varying-scale TIN finished!\n');
