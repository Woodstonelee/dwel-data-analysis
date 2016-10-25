% read two point clouds of apparent reflectances and FWHM at the two
% wavelengths to calculate pgap for leaves and branches separately.
clear;

% ******************************************************************************
% Arguments for inputs
nirptsfile = '/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_C/HFHD_20140919_C_1064_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points.txt';
swirptsfile = '/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_C/HFHD_20140919_C_1548_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points.txt';
% nirptsfile = '/home/zhanli/Workspace/data/dwel-processing/hfhd20140919/hfhd20140919-ptcl-apprefl-20141211/HFHD_20140919_C_1064_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points.txt';
% swirptsfile = '/home/zhanli/Workspace/data/dwel-processing/hfhd20140919/hfhd20140919-ptcl-apprefl-20141211/HFHD_20140919_C_1548_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points.txt';

% pcinfo image file for mask input, to exclude missing shots, bad shots and
% etc. in the pgap caculatiion. 
nirpcinfoimagefile = '/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_C/HFHD_20140919_C_1064_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_pcinfo.img';
swirpcinfoimagefile = '/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_C/HFHD_20140919_C_1548_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_pcinfo.img';

%nsamples = 1022;
%nlines = 3142;

i_scale = 1000.0;
pulse_fwhm_nir = 3.6469;
pulse_fwhm_swir = 3.6469;

scanres = 2.0e-3/pi*180; % deg
hbinsize = 0.5; % meter
zenbinsize = 5; % degrees
minzen = 5; % deg
maxzen = 70; % deg
maxh = 50;
ndi_thresh = 0.45;

leaf_refl = [0.413, 0.284];
wood_refl = [0.541, 0.540];

% Arguments for outputs
ptsndifile = ['/projectnb/echidna/lidar/DWEL_Processing/HF2014/' ...
              'Hardwood20140919/HFHD_20140919_C/HFHD_20140919_C_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points_ndi.txt'];

outdir = ['/projectnb/echidna/lidar/DWEL_Processing/HF2014/' ...
              'Hardwood20140919/HFHD_20140919_C/pgap2'];
% ******************************************************************************

fprintf('Read information from pcinfo image ... \n');

% read pcinfo image file and get image dimension for azimuth and zenith
% range, and also mask.
nirhdr = envihdrread([nirpcinfoimagefile,'.hdr']);
temp = multibandread(nirpcinfoimagefile, [nirhdr.lines, nirhdr.samples, ...
                    nirhdr.bands], nirhdr.data_type.matlab, nirhdr.header_offset, ...
                     nirhdr.interleave, nirhdr.byte_order.matlab, {'Band', ...
                    'Direct', [9, 10, 13]});
nirmask = logical(temp(:,:,3));
imagezen = temp(:,:,1)/100;
imageaz = temp(:,:,2)/100;
clear temp;
swirhdr = envihdrread([swirpcinfoimagefile,'.hdr']);
temp = multibandread(swirpcinfoimagefile, [swirhdr.lines, swirhdr.samples, ...
                    swirhdr.bands], swirhdr.data_type.matlab, swirhdr.header_offset, ...
                     swirhdr.interleave, swirhdr.byte_order.matlab, {'Band', ...
                    'Direct', [9, 10, 13]});
swirmask = logical(temp(:,:,3));
imagezen = temp(:,:,1)/100;
imageaz = temp(:,:,2)/100;
clear temp;

nsamples = nirhdr.samples;
nlines = nirhdr.lines;
mask = logical(nirmask) & logical(swirmask);

fprintf(['Read point cloud and look for common points between two wavelengths ' ...
         '... \n']);

% read point cloud data
fid = fopen(nirptsfile, 'r');
nirpts = textscan(fid, repmat('%f', 1, 17), 'HeaderLines', 3, 'Delimiter', ',');
fclose(fid);
nirpts = cell2mat(nirpts);
fid = fopen(swirptsfile, 'r');
swirpts = textscan(fid, repmat('%f', 1, 17), 'HeaderLines', 3, 'Delimiter', ',');
fclose(fid);
swirpts = cell2mat(swirpts);

% suppress all negative intensity to zero
tmplogic = nirpts(:, 4)<0;
nirpts(tmplogic, 4)=0;
tmplogic = swirpts(:, 4)<0;
swirpts(tmplogic, 4)=0;
% remove all zero locations
tmplogic = nirpts(:, 1)==0 & nirpts(:,2)==0 & nirpts(:,3)==0 & nirpts(:,4)==0;
nirptsvalidind = find(~tmplogic);
tmplogic = swirpts(:,1)==0 & swirpts(:,2)==0 & swirpts(:,3)==0 & swirpts(:,4)==0;
swirptsvalidind = find(~tmplogic);
% find the common points between 1064 and 1548 by checking their return
% numbers (1st or 2nd or ... return) and their angular positions. 
% If the three fields are the same, we think there is common point pair.
% !!! This might NOT BE TRUE, e.g. when two peaks are extracted from the
% 1548 nm while only one peak from the 1064 nm. !!!
[~, inir, iswir] = intersect([nirpts(nirptsvalidind, 5:6), nirpts(nirptsvalidind,13:14)], [swirpts(swirptsvalidind, 5:6), swirpts(swirptsvalidind,13:14)], 'rows');
% NDI of each common point
nirptscmind = nirptsvalidind(inir);
swirptscmind = swirptsvalidind(iswir);
pts_ndi = (nirpts(nirptscmind, 4)-swirpts(swirptscmind, 4))./(nirpts(nirptscmind, 4)+swirpts(swirptscmind, 4));
pts_mean = (nirpts(nirptscmind, 1:3)+swirpts(swirptscmind, 1:3))/2;

cmpts = [pts_mean, pts_ndi, ...
                    nirpts(nirptscmind,4), swirpts(swirptscmind, 4), ...
                    nirpts(nirptscmind,5:6), (nirpts(nirptscmind,9)+ ...
                    swirpts(swirptscmind,9))/2.0, nirpts(nirptscmind,9)- ...
                    swirpts(swirptscmind,9), (nirpts(nirptscmind, 10:11)+ ...
                                              swirpts(swirptscmind, 10:11))/2, ...
                    nirpts(nirptscmind, 13:14), nirpts(nirptscmind, 16:17), ...
                    swirpts(swirptscmind, 16:17)];

% lower and upper limit of intensity to scale the color of 1064 (green) and
% 1548 (red).
% if empty [] given, actual minimum/maximum of 1064/1548 intensity will be
% used to scale the color.
minI1064 = 0; 
maxI1064 = [];
minI1548 = 0;
maxI1548 = [];

% add three columns of RGB for color-composite point cloud
if isempty(minI1064)
    minI1064 = min(nirpts(nirptscmind,4));
end
if isempty(maxI1064)
    maxI1064 = max(nirpts(nirptscmind,4));
end
NormIntensity1064 = (nirpts(nirptscmind,4)-minI1064)/(maxI1064-minI1064);
tmp = stretchlim(NormIntensity1064);
NormIntensity1064 = imadjust(NormIntensity1064, tmp, []);
%NormIntensity1064(NormIntensity1064 > 1) = 1;
if isempty(minI1548)
    minI1548 = min(swirpts(swirptscmind,4));
end
if isempty(maxI1548)
    maxI1548 = max(swirpts(swirptscmind,4));
end
NormIntensity1548 = (swirpts(swirptscmind,4)-minI1548)/(maxI1548-minI1548);
tmp = stretchlim(NormIntensity1548);
NormIntensity1548 = imadjust(NormIntensity1548, tmp, []);
%NormIntensity1548(NormIntensity1548 > 1) = 1;
rgbcc = zeros(size(cmpts, 1), 3);
rgbcc(:, 1) = round(NormIntensity1548*255);
rgbcc(:, 2) = round(NormIntensity1064*255);

fprintf('Write common points ... \n');

% write NDI points to an ascii file
fid = fopen(ptsndifile, 'w');
infid = fopen(nirptsfile, 'r');
linestr = fgetl(infid);
fprintf(fid, '%s; NDI\n', linestr);
linestr = fgetl(infid);
fprintf(fid, '%s\n', linestr);
fclose(infid);
fprintf(fid, ['X,Y,Z,NDI,d_I_nir,d_I_swir,Return_Number,Number_of_Returns,' ...
              'range_mean, range_nir_minus_swir,theta,phi,Sample,Line,I_nir,FWHM_nir,I_swir,FWHM_swir,R,G,B\n']);
fprintf(fid, [repmat('%.3f,',1,6), repmat('%d,',1,2), repmat('%.3f,',1,4), ...
              repmat('%d,',1,2),repmat('%.3f,',1,4), repmat('%d,',1,3),'\b\n'], ([cmpts,rgbcc])');
fclose(fid);

fprintf('Calculate intercept fraction of leaves and woody returns ... \n');

cmpts_nhit = 8;
cmpts_sample=13;
cmpts_line=14;
cmpts_inir = 15;
cmpts_wnir = 16;
cmpts_iswir = 17;
cmpts_wswir = 18;
cmpts_r = 9;
cmpts_ndi = 4;
cmpts_zen = 11;

linearind = sub2ind([nlines, nsamples, 3], cmpts(:,cmpts_line), cmpts(:, ...
                                                  cmpts_sample), cmpts(:,cmpts_nhit-1));

maxnhit = max(cmpts(:, cmpts_nhit));
nir_I = zeros(nlines, nsamples, maxnhit);
nir_fwhm = zeros(nlines, nsamples, maxnhit);
swir_I = zeros(nlines, nsamples, maxnhit);
swir_fwhm = zeros(nlines, nsamples, maxnhit);
range = zeros(nlines, nsamples, maxnhit);
ndi = zeros(nlines, nsamples, maxnhit);
nir_refl = ones(nlines, nsamples, maxnhit);
swir_refl = ones(nlines, nsamples, maxnhit);

nir_I(linearind) = cmpts(:, cmpts_inir);
nir_fwhm(linearind) = cmpts(:, cmpts_wnir);
swir_I(linearind) = cmpts(:, cmpts_iswir);
swir_fwhm(linearind) = cmpts(:, cmpts_wswir);
range(linearind) = cmpts(:, cmpts_r);
ndi(linearind) = cmpts(:, cmpts_ndi);

% classifiy hits by thresholding ndi and assign appropriate reflectance
leafflag = ndi >= ndi_thresh;
nir_refl(leafflag) = leaf_refl(1);
swir_refl(leafflag) = leaf_refl(2);
nir_refl(~leafflag & ndi>0) = wood_refl(1);
swir_refl(~leafflag & ndi>0) = wood_refl(2);

%phit_raw = zeros(nlines, nsamples, 2);

phaseval = [0.2, 0.2];
pgapsc = true;
% calculate Pgap from apparent reflectance for each point/scattering
% event. Pgap is the gap probability from the instrument to the point. 
% two columns: [pgap_nir, pgap_swir] for each point
phit_raw = zeros(size(cmpts, 1), 2); 
% store interception fraction of each individual shot at the farthest range
phit_image = zeros(nlines, nsamples, 2);
tmp = nir_I.*nir_fwhm./nir_refl/(pulse_fwhm_nir*i_scale);
tmp(tmp>1) = 1;
tmp(tmp<0) = 0;
tmp  = cumsum(tmp, 3);
phit_raw(:,1) = tmp(linearind);
phit_image(:,:,1) = tmp(:,:,3);
tmp = swir_I.*swir_fwhm./swir_refl/(pulse_fwhm_swir*i_scale);
tmp(tmp>1) = 1;
tmp(tmp<0) = 0;
tmp  = cumsum(tmp, 3);
phit_raw(:,2) = tmp(linearind);
phit_image(:,:,2) = tmp(:,:,3);
clear tmp;

phit_raw(phit_raw>1) = 1;
phit_image(phit_image>1) = 1;

phit_image_sc = phit_image;
if pgapsc
    tmpflag = phit_raw(:,1) >= phaseval(1);
    phit_raw(tmpflag, 1) = 1.0;
    phit_raw(~tmpflag, 1) = phit_raw(~tmpflag, 1)/phaseval(1);
    tmpflag = phit_raw(:,2) >= phaseval(2);
    phit_raw(tmpflag, 2) = 1.0;
    phit_raw(~tmpflag, 2) = phit_raw(~tmpflag, 2)/phaseval(2);

    tmp = phit_image(:,:,1);
    tmpflag = tmp >= phaseval(1);
    tmp(tmpflag) = 1.0;
    tmp(~tmpflag) = tmp(~tmpflag)/phaseval(1);
    phit_image_sc(:,:,1) = tmp;
    tmp = phit_image(:,:,2);
    tmpflag = tmp >= phaseval(2);
    tmp(tmpflag) = 1.0;
    tmp(~tmpflag) = tmp(~tmpflag)/phaseval(2);
    phit_image_sc(:,:,2) = tmp;
end

save(fullfile(outdir, 'dualpts2pgap.mat'), 'cmpts', 'phit_raw', 'pulse_fwhm_nir', ...
     'pulse_fwhm_swir', 'leaf_refl', 'wood_refl');

heights = 0:hbinsize:maxh;
nzenithbins = fix((maxzen-minzen)/zenbinsize);
midzeniths = (0:nzenithbins-1)*zenbinsize + zenbinsize/2;
pgapz_total_nir = ones(nzenithbins, length(heights));
pgapz_leaf_nir = ones(nzenithbins, length(heights));
pgapz_branch_nir = ones(nzenithbins, length(heights));
pgapz_total_swir = ones(nzenithbins, length(heights));
pgapz_leaf_swir = ones(nzenithbins, length(heights));
pgapz_branch_swir = ones(nzenithbins, length(heights));

fprintf('Calculate Pgap ... \n');

%npulses = fix(zenbinsize/scanres)*nlines;
for zen=1:1:nzenithbins
    zenind = cmpts(:,cmpts_zen) > midzeniths(zen)-zenbinsize/2.0 & cmpts(:,cmpts_zen) ...
             < midzeniths(zen)+zenbinsize/2.0;
    nzen = sum(zenind);
    % calculate number of valid pulses
    npulses = imagezen > midzeniths(zen)-zenbinsize/2.0 & imagezen ...
             < midzeniths(zen)+zenbinsize/2.0 & mask;
    npulses = sum(npulses(:));
    if nzen > 0
        leafind = cmpts(:,cmpts_ndi)>=ndi_thresh;
        for hi =1:1:length(heights)
            hind = cmpts(:,3)<=heights(hi);
            pgapz_total_nir(zen, hi) = 1.0 - sum(phit_raw(zenind & hind, 1))/npulses;
            pgapz_total_swir(zen, hi) = 1.0 - sum(phit_raw(zenind & hind, 2))/npulses;
            pgapz_leaf_nir(zen, hi) = 1.0 - sum(phit_raw(zenind & hind & leafind,1))/npulses;
            pgapz_leaf_swir(zen, hi) = 1.0 - sum(phit_raw(zenind & hind & leafind,2))/npulses;
            pgapz_branch_nir(zen, hi) = 1.0 - sum(phit_raw(zenind & hind & ~leafind,1))/npulses;
            pgapz_branch_swir(zen, hi) = 1.0 - sum(phit_raw(zenind & hind & ~leafind,2))/npulses;
        end
    end
end

save(fullfile(outdir, 'pgap.mat'), 'midzeniths', 'heights', 'pgapz_total_nir', 'pgapz_total_swir', 'pgapz_leaf_nir', 'pgapz_leaf_swir', 'pgapz_branch_nir', 'pgapz_branch_swir');

tmpflag = isnan(sum(pgapz_total_nir, 1)) | isnan(sum(pgapz_total_swir, 1)) | ...
          isnan(sum(pgapz_leaf_nir, 1)) | isnan(sum(pgapz_leaf_swir, 1)) | ...
          isnan(sum(pgapz_branch_nir, 1)) | isnan(sum(pgapz_branch_swir, 1));
heights = heights(~tmpflag);
pgapz_total_nir = pgapz_total_nir(:, ~tmpflag);
pgapz_leaf_nir = pgapz_leaf_nir(:, ~tmpflag);
pgapz_branch_nir = pgapz_branch_nir(:, ~tmpflag);
pgapz_total_swir = pgapz_total_swir(:, ~tmpflag);
pgapz_leaf_swir = pgapz_leaf_swir(:, ~tmpflag);
pgapz_branch_swir = pgapz_branch_swir(:, ~tmpflag);

fid = fopen(fullfile(outdir, 'midzeniths.txt'), 'w');
fprintf(fid, '%.3f\n', midzeniths);
fclose(fid);
fid = fopen(fullfile(outdir, 'heights.txt'), 'w');
fprintf(fid, '%.3f\n', heights);
fclose(fid);
fid = fopen(fullfile(outdir, 'pgapz_total_nir.txt'), 'w');
fprintf(fid, [repmat('%.3f,', 1, length(heights)-1), '%.3f\n'], pgapz_total_nir');
fclose(fid);
fid = fopen(fullfile(outdir, 'pgapz_leaf_nir.txt'), 'w');
fprintf(fid, [repmat('%.3f,', 1, length(heights)-1), '%.3f\n'], pgapz_leaf_nir');
fclose(fid);
fid = fopen(fullfile(outdir, 'pgapz_branch_nir.txt'), 'w');
fprintf(fid, [repmat('%.3f,', 1, length(heights)-1), '%.3f\n'], pgapz_branch_nir');
fclose(fid);
fid = fopen(fullfile(outdir, 'pgapz_total_swir.txt'), 'w');
fprintf(fid, [repmat('%.3f,', 1, length(heights)-1), '%.3f\n'], pgapz_total_swir');
fclose(fid);
fid = fopen(fullfile(outdir, 'pgapz_leaf_swir.txt'), 'w');
fprintf(fid, [repmat('%.3f,', 1, length(heights)-1), '%.3f\n'], pgapz_leaf_swir');
fclose(fid);
fid = fopen(fullfile(outdir, 'pgapz_branch_swir.txt'), 'w');
fprintf(fid, [repmat('%.3f,', 1, length(heights)-1), '%.3f\n'], pgapz_branch_swir');
fclose(fid);


% % plot pgap
% figure('Name', 'Pgap, leaves');
% plot(pgapz_leaf(1,:), heights, '-r');
% hold on;
% for i=2:nzenithbins
%     plot(pgapz_leaf(i,:), heights);
% end
% figure('Name', 'Pgap, branches');
% plot(pgapz_branch(1,:), heights, '-r');
% hold on;
% for i=2:nzenithbins
%     plot(pgapz_branch(i,:), heights);
% end

% calculate area index and profile
% David Jupp's linear model
%[LAIprofile, MLA, LAVD] = LM_pgap2profile(midzeniths,heights,pgapz_leaf);
%[BAIprofile, MBA, BAVD] = LM_pgap2profile(midzeniths,heights,pgapz_branch);

