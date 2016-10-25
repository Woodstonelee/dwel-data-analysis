%
% Plot leaf area profile and branch area profile from python program
% "get_plant_profiles.py"
% 
% Zhan Li, zhanli86@bu.edu
% Created: 20141028
% Last modified: 20141212

datadir = '/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_C/pgap2';

nir_totalpfile = 'profile_total_nir.txt';
nir_laipfile = 'profile_leaf_nir.txt';
nir_baipfile = 'profile_branch_nir.txt';

swir_totalpfile = 'profile_total_swir.txt';
swir_laipfile = 'profile_leaf_swir.txt';
swir_baipfile = 'profile_branch_swir.txt';

fid = fopen(fullfile(datadir,nir_totalpfile), 'r');
data = textscan(fid, repmat('%f ', 1, 4), 'Delimiter', ',');
fclose(fid);
nir_totalprofile = cell2mat(data);
fid = fopen(fullfile(datadir,nir_laipfile), 'r');
data = textscan(fid, repmat('%f ', 1, 4), 'Delimiter', ',');
fclose(fid);
nir_laiprofile = cell2mat(data);
fid = fopen(fullfile(datadir,nir_baipfile), 'r');
data = textscan(fid, repmat('%f ', 1, 4), 'Delimiter', ',');
fclose(fid);
nir_baiprofile = cell2mat(data);

fid = fopen(fullfile(datadir,swir_totalpfile), 'r');
data = textscan(fid, repmat('%f ', 1, 4), 'Delimiter', ',');
fclose(fid);
swir_totalprofile = cell2mat(data);
fid = fopen(fullfile(datadir,swir_laipfile), 'r');
data = textscan(fid, repmat('%f ', 1, 4), 'Delimiter', ',');
fclose(fid);
swir_laiprofile = cell2mat(data);
fid = fopen(fullfile(datadir,swir_baipfile), 'r');
data = textscan(fid, repmat('%f ', 1, 4), 'Delimiter', ',');
fclose(fid);
swir_baiprofile = cell2mat(data);

% plot cumulative area
figure();
plot(nir_totalprofile(:,2), nir_totalprofile(:,1), '-xk', 'LineWidth',2);
hold on;
plot(nir_laiprofile(:,2), nir_laiprofile(:,1), '-xg', 'LineWidth',2);
plot(nir_baiprofile(:,2), nir_baiprofile(:,1), '-xr', 'LineWidth',2);
plot(swir_totalprofile(:,2), swir_totalprofile(:,1), '-ok', 'LineWidth',2);
plot(swir_laiprofile(:,2), swir_laiprofile(:,1), '-og', 'LineWidth',2);
plot(swir_baiprofile(:,2), swir_baiprofile(:,1), '-or', 'LineWidth',2);
title('Cumulative Vegetation Area Index of leaves and woody materials');
xlabel('Vegetation Area Index (m^{-2}/m^{-2})');
ylabel('Height (meter)');
ylim([0,35]);
legend({'NIR, total', 'NIR, leaves', 'NIR, woody', 'SWIR, total', 'SWIR, leaves', ...
       'SWIR, woody'}, 'Location', 'southeast');
legend('boxoff');
export_fig(fullfile(datadir, 'CumVAI.png'), '-png', '-r300', '-painters');

% plot favd, foliage area volume density
figure();
plot(nir_totalprofile(:,4), nir_totalprofile(:,1), '-xk', 'LineWidth',2);
hold on;
plot(nir_laiprofile(:,4), nir_laiprofile(:,1), '-xg', 'LineWidth',2);
plot(nir_baiprofile(:,4), nir_baiprofile(:,1), '-xr', 'LineWidth',2);
plot(swir_totalprofile(:,4), swir_totalprofile(:,1), '-ok', 'LineWidth',2);
plot(swir_laiprofile(:,4), swir_laiprofile(:,1), '-og', 'LineWidth',2);
plot(swir_baiprofile(:,4), swir_baiprofile(:,1), '-or', 'LineWidth',2);
title('Vegetation area profile of leaves and woody materials');
xlabel('Vegetation area profile (m^{-2}/m^{-3})');
ylabel('Height (meter)');
ylim([0,35]);
legend({'NIR, total', 'NIR, leaves', 'NIR, woody', 'SWIR, total', 'SWIR, leaves', ...
       'SWIR, woody'}, 'Location', 'southeast');
legend('boxoff');
export_fig(fullfile(datadir, 'profile.png'), '-png', '-r300', '-painters');

% plot ratio of leaf and branch area to total area
figure();
plot(nir_laiprofile(:,2)./nir_totalprofile(:,2), nir_totalprofile(:,1), '-xg', ...
     'LineWidth', 2);
hold on;
plot(nir_baiprofile(:,2)./nir_totalprofile(:,2), nir_totalprofile(:,1), '-xr', ...
     'LineWidth', 2);
% plot((nir_laiprofile(:,2)+nir_baiprofile(:,2))./nir_totalprofile(:,2), nir_totalprofile(:,1), '-k', ...
%      'LineWidth', 2);
plot(swir_laiprofile(:,2)./swir_totalprofile(:,2), swir_totalprofile(:,1), '-og', ...
     'LineWidth', 2);
plot(swir_baiprofile(:,2)./swir_totalprofile(:,2), swir_totalprofile(:,1), '-or', ...
     'LineWidth', 2);
% plot((swir_laiprofile(:,2)+swir_baiprofile(:,2))./swir_totalprofile(:,2), swir_totalprofile(:,1), '--k', ...
%      'LineWidth', 2);
title('Cumulative vegetation area proportion of leaves and woody materials');
xlabel('Vegetation Area Proportion');
ylabel('Height (meter)');
ylim([0,35]);
legend({'NIR, leaves', 'NIR, woody', 'SWIR, leaves', ...
       'SWIR, woody'}, 'Location', 'northeast');
legend('boxoff');
export_fig(fullfile(datadir, 'CumVAIRatio.png'), '-png', '-r300', '-painters');

% plot ratio of leaf and branch favd to total favd
figure();
tmp = nir_laiprofile(:,4)./nir_totalprofile(:,4);
tmpflag = tmp<=1 & ~isnan(tmp); 
plot(tmp(tmpflag), nir_totalprofile(tmpflag,1), '-xg', ...
     'LineWidth', 2);
hold on;
tmp = nir_baiprofile(:,4)./nir_totalprofile(:,4);
tmpflag = tmp<=1 & ~isnan(tmp);
plot(tmp(tmpflag), nir_totalprofile(tmpflag,1), '-xr', ...
     'LineWidth', 2);
% plot((nir_laiprofile(:,4)+nir_baiprofile(:,4))./nir_totalprofile(:,4), nir_totalprofile(:,1), '-k', ...
%      'LineWidth', 2);
tmp = swir_laiprofile(:,4)./swir_totalprofile(:,4);
tmpflag = tmp<=1 & ~isnan(tmp);
plot(tmp(tmpflag), swir_totalprofile(tmpflag,1), '-og', ...
     'LineWidth', 2);
tmp = swir_baiprofile(:,4)./swir_totalprofile(:,4);
tmpflag = tmp<=1 & ~isnan(tmp); 
plot(tmp(tmpflag), swir_totalprofile(tmpflag,1), '-or', ...
     'LineWidth', 2);
% plot((swir_laiprofile(:,4)+swir_baiprofile(:,4))./swir_totalprofile(:,4), swir_totalprofile(:,1), '--k', ...
%      'LineWidth', 2);
title('Vegetation area volume density proportion of leaves and woody materials');
xlabel('Vegetation area volume density proportion');
ylabel('Height (meter)');
ylim([0,35]);
legend({'NIR, leaves', 'NIR, woody', 'SWIR, leaves', ...
       'SWIR, woody'}, 'Location', 'northeast');
legend('boxoff');
export_fig(fullfile(datadir, 'profileratio.png'), '-png', '-r300', '-painters');


% subplot(1,2,1)
% plot(laiprofile(:,2), laiprofile(:,1), '-g');
% hold on;
% plot(baiprofile(:,2), baiprofile(:,1), '-r');
% subplot(1,2,2)
% plot(laiprofile(:,4), laiprofile(:,1), '-g');
% hold on;
% plot(baiprofile(:,4), baiprofile(:,1), '-r');
