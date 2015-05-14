% read points and ndi. calculate pgap for leaves and branches separately.
clear;

ndiptsfilename = '/home/zhanli/Workspace/data/dwel-processing/hfhd20140919/hfhd20140919-ptcl/HFHD_20140919_C_cube_bsfix_pxc_update_atp4_ptcl_points_ndirgb_0.2.txt';
binsize = 4e-3/pi*180; % deg
hbinsize = 0.5; % meter
zenbinsize = 5; % degrees
minzen = 5; % deg
maxzen = 70; %deg
maxh = 50;
ndi_thresh = 0.2;

% X,Y,Z,d_I,R,G,B,range,theta,phi,number_of_returns,sample,line (13)
fid = fopen(ndiptsfilename, 'r');
data = textscan(fid, '%f %f %f %f %f %f %f %f %f %f %f %f %f', 'HeaderLines', 3, 'Delimiter', ',');
fclose(fid);
data = cell2mat(data);

heights = 0:hbinsize:maxh;
nzenithbins = fix((maxzen-minzen)/zenbinsize);
midzeniths = (0:nzenithbins-1)*zenbinsize + zenbinsize/2;
pgapz_leaf = ones(nzenithbins, length(heights));
pgapz_branch = ones(nzenithbins, length(heights));

npulses = fix(360/binsize*zenbinsize/binsize); % number of theoretical outgoing pulses in one zenith ring
for zen=1:1:nzenithbins
    zenind = data(:,9) > midzeniths(zen)-zenbinsize/2.0 & data(:,9) < midzeniths(zen)+zenbinsize/2.0;
    if sum(zenind) > 0
        pointdata = data(zenind, :);
        w = 1.0./pointdata(:,8);
        leafind = pointdata(:,4)>ndi_thresh;
        for hi =1:1:length(heights)
            hits_leaf = sum(w(leafind & pointdata(:,3)<= heights(hi)));
            pgapz_leaf(zen, hi) = 1.0 - hits_leaf/npulses;
            hits_branch = sum(w(~leafind & pointdata(:,3)<=heights(hi)));
            pgapz_branch(zen, hi) = 1.0 - hits_branch/npulses;
        end
    end
end

fid = fopen('midzeniths.txt', 'w');
fprintf(fid, '%.3f\n', midzeniths);
fclose(fid);
fid = fopen('heights.txt', 'w');
fprintf(fid, '%.3f\n', heights);
fclose(fid);
fid = fopen('pgapz_leaf.txt', 'w');
fprintf(fid, [repmat('%.3f,', 1, length(heights)-1), '%.3f\n'], pgapz_leaf');
fclose(fid);
fid = fopen('pgapz_branch.txt', 'w');
fprintf(fid, [repmat('%.3f,', 1, length(heights)-1), '%.3f\n'], pgapz_branch');
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