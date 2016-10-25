% setup for the script files
script1 = '/usr3/graduate/zhanli86/Programs/TIES-TLS/Script1_CvtPtsFmt.m';
script2 = '/usr3/graduate/zhanli86/Programs/TIES-TLS/Script2_FilteringVarTIN.m';

% inputs and parameters to be set for the sequence of four/five scripts.
% input point cloud file of single scan, full file name
ScanPtsFile = '/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points/HFHD_20140919_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_return.txt';
% a temporary folder to store all intermediate files, no trailing path seperator.
TmpDir = '/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points/test-points-dem';

% parameters for Script2, filtering non-ground points and output
% ground points. 
RefineGround = false;

% run script1
fprintf('\nRunning %s ...\n\n', script1);
[ScanPtsPathName, ScanPtsFileName, ext] = fileparts(ScanPtsFile);
InPtsPathName = TmpDir;
InPtsFileName = [ScanPtsFileName, '_xyz.txt'];
ScanPtsFileName = [ScanPtsFileName, ext];
run(script1);

% run script2
fprintf('\nRunning %s ...\n\n', script2);
GroundPtsPathName = InPtsPathName;
GroundPtsFileName = [InPtsFileName(1:end-4), '_ground.txt'];
run(script2);

% extract the whole lines of ground points according to the line
% numbers.
% read line numbers of ground points
fid = fopen(fullfile(GroundPtsPathName, [GroundPtsFileName, '.lnum']));
line_num = textscan(fid, '%d');
fclose(fid);
line_num = cell2mat(line_num);

fid = fopen(ScanPtsFile);
% data = textscan(fid, repmat('%f', 1, 19), 'HeaderLines', 3, 'Delimiter', ',');
data = textscan(fid, '%s', 'HeaderLines', 3);
fclose(fid);
data = data{1};

[ScanPtsPathName, ScanPtsFileName, ext] = fileparts(ScanPtsFile);
fid = fopen(fullfile(ScanPtsPathName, [ScanPtsFileName, '_ground', ext]), 'w');
infid = fopen(ScanPtsFile);
tline = fgetl(infid);
fprintf(fid, '%s [Ground point extraction by TIES-TLS]\n', tline);
for i = 2:3
    tline = fgetl(infid);
    fprintf(fid, '%s\n', tline);
end
for i = 1:length(line_num)
    fprintf(fid, '%s\n', data{line_num(i)});
end
fclose(fid);
fclose(infid);

% label the original point cloud as ground and non-ground points
flag = zeros(size(data));
flag(line_num) = 1;
fid = fopen(fullfile(ScanPtsPathName, [ScanPtsFileName, '_grdlabel', ext]), 'w');
infid = fopen(ScanPtsFile);
tline = fgetl(infid);
fprintf(fid, '%s [Ground points labeling by TIES-TLS]\n', tline);
tline = fgetl(infid);
fprintf(fid, '%s\n', tline);
tline = fgetl(infid);
fprintf(fid, '%s,grd_label\n', tline);
for i = 1:length(data)
    fprintf(fid, '%s,%d\n', data{i}, flag(i));
end
fclose(fid);
fclose(infid);
