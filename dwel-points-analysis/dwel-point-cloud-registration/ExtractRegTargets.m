% This script extracts registration targets (e.g. reflective cylinders or
% balls) from DWEL point clouds based on ROIs of targets identified from DWEL
% scanning images.
%
% Zhan Li, zhanli86@bu.edu
% Created: 2014/08/27
% Last revision: 2014/08/27
%

% % input ROI ascii file from ENVI
% roi_filename = ['/projectnb/echidna/lidar/DWEL_Processing/Brisbane2013Aug/' ...
%                 'Brisbane2013_BFP/Aug3_BFP_C_1548_Cylinders.txt'];
% % input DWEL point cloud file generated from DWEL processing program. This
% % file should include the row and column in the scanning image where a point
% % is extracted from. 
% pts_filename = ['/projectnb/echidna/lidar/DWEL_Processing/Brisbane2013Aug/' ...
%                 'Brisbane2013_BFP/Aug3_BFP_C/' ...
%                 'Aug3_BFP_C_1548_Cube_NadirCorrect_Aligned_nu_basefix_satfix_pfilter_b32r04_at_project_ptcl_points.txt'];
% % output file name of extracted targets. 
% target_filename = ['/projectnb/echidna/lidar/DWEL_Processing/Brisbane2013Aug/' ...
%                    'Brisbane2013_BFP/Aug3_BFP_C_1548_Cylinders_Extraction.txt'];

% open roi file
roi_fid = fopen(roi_filename, 'r');
% read roi file and parse the file contents
l = 0;
% skip the first 1 line
while l < 1
    tline = fgetl(roi_fid);
    l = l + 1;
end
% read the 2nd line
tline = fgetl(roi_fid);
nroi = sscanf(tline, '; Number of ROIs: %d');
if isempty(nroi)
    fprintf('ROI ascii file content error: cannot read number of ROIs. \n');
    fclose(roi_fid);
    return
end
% number of pixels per roi
npts_roi = zeros(nroi, 1);
% a struct array to record all pixel rows and columns in each roi. 
roi = struct('count', {}, 'row', {}, 'col', {});
tline = fgetl(roi_fid);
while ischar(tline) && tline(1) == ';'
    if strfind(tline, '; ROI name:')
        ind = sscanf(tline, '; ROI name: Region #%d');
        if isempty(ind)
            fprintf('ROI ascii file content error: cannot find a ROI name.\n');
            fclose(roi_fid);
            return
        end
        tline = fgetl(roi_fid);
        tline = fgetl(roi_fid);
        count = sscanf(tline, '; ROI npts: %d');
        if isempty(count)
            fprintf(['ROI ascii file content error: cannot read number of ' ...
                     'pixels in a ROI.\n']);
            fclose(roi_fid);
            return
        end
        roi(ind).count = count;
        roi(ind).row = zeros(count, 1);
        roi(ind).col = zeros(count, 1);
    end
    tline = fgetl(roi_fid);
end

% start reading pixel locations
for i=1:nroi
    % skip empty lines
    while ischar(tline) && isempty(tline)
        tline = fgetl(roi_fid);
    end
    pts = sscanf(tline, '%d %d %d %d');
    if isempty(pts) || length(pts) ~= 4
        fprintf(['ROI ascii file content error: pixel location reading ' ...
                 'unexpected.\n']);
        fprintf(tline);
        fclose(roi_fid);
        return
    end
    roi(i).row(1) = pts(3);
    roi(i).col(1) = pts(2);
    for p=2:roi(i).count
        tline = fgetl(roi_fid);
        pts = sscanf(tline, '%d %d %d %d');
        if isempty(pts) || length(pts) ~= 4
            fprintf(['ROI ascii file content error: pixel location reading ' ...
                     'unexpected.\n']);
            fprintf(tline)
            fclose(roi_fid);
            return
        end
        roi(i).row(p) = pts(3);
        roi(i).col(p) = pts(2);
    end
    tline = fgetl(roi_fid);
end
fclose(roi_fid);
% create an array for all pixels from all ROIs
npts = sum(npts_roi(:));
roi_all = zeros(npts, 3);
tmpind = 1;
for i=1:nroi
    roi_all(tmpind:tmpind+roi(i).count-1, :) = [roi(i).row(:), roi(i).col(:), ...
                   ones(roi(i).count, 1)*i];
    tmpind = tmpind + roi(i).count;
end

% open the point cloud file
pts_fid = fopen(pts_filename, 'r');
data = textscan(pts_fid, repmat('%f ', 1, 14), 'HeaderLines', '3', 'Delimiter', ...
                {'', '\b', '\t', ','});
fclose(pts_fid);
% x = data{1};
% y = data{2};
% z = data{3};
% intensity = data{4};
% numreturns = data{6};
% range = data{9};
% theta = data{10};
% phi = data{11};
% column = data{12};
% row = data{13};
% clear data;
ptsdata = cell2mat(data);
clear data;

% remove points from multi-return waveforms
tmpflag = ptsdata(:, 6) == 1;
ptsdata = ptsdata(tmpflag, :);

% find the points that belong to the ROIs
[lia, locb] = ismember([ptsdata(:, 13), ptsdata(:, 12)], roi_all(:, 1:2), 'rows');
ptsdata = ptsdata(lia, :);
locb = locb(lia);

roipts = [ptsdata, roi_all(locb, 3)];
roitargets = zeros(nroi, 5);
for i=1:nroi
    tmpflag = roipts(:,15)==i;
    roitargets(i, :)=[mean(roipts(tmpflag, 1)), mean(roipts(tmpflag, 2)), ...
                      mean(roipts(tmpflag, 3)), mean(roipts(tmpflag, 4)), ...
                      std(roipts(tmpflag, 4))];
end
outfid = fopen(target_filename, 'w');
fprintf(outfid, 'x,y,z,intensity,sd_intensity\n');
fprintf(outfid, [repmat('%.3f,', 1, 4), '%.3f\n'], roitargets');
fclose(outfid);