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

    %----------------------------------
    % Iputs needed to be set beforehand
    % dwel_pts_file, input DWEL point cloud ASCII file name.
    % out_dir, directory for the filtering outputs.

    options = struct('scale', [4.0000; 2.0000; 1.0000; 0.5000], ...
                     'door', [3.0000; 1.5000; 0.5000; 0.2000], ...
                     'refine_ground', false, ...
                     'ground_extra', false, ...
                     'refine_single_scan', false, ...
                     'ransac_t', 0.25, ...
                     'ransac_grid', 10, ...
                     'max_slope', 45, ...
                     'center', []);

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
    ground_extra_flag = options.ground_extra;
    refine_single_scan = options.refine_single_scan;
    ransac_t_rg = options.ransac_t;
    ransac_grid_rg = options.ransac_grid;
    extent_center = options.center;
    max_slope = options.max_slope;

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
    gpfid=fopen(fullfile(GroundPtsPathName, GroundPtsFileName), 'r');
    rawdata=textscan(gpfid,'%f %f %f');
    fclose(gpfid);
    datax=rawdata{1};
    datay=rawdata{2};
    dataz=rawdata{3};
    clear rawdata;

    ground_extra = [];

    if refine_ground
        fprintf('Refine ground points by fitting planes with RANSAC to gridded point cloud.\n');

        npts = length(datax);

        t = ransac_t_rg;
        grid_size = ransac_grid_rg;
        if isempty(extent_center)
            % center of the ground extent, [x, y]
            extent_center = [0.5*(min(datax)+max(datax)), 0.5*(min(datay)+max(datay))];
        end
        fprintf('\tGrid size within which a RANSAC plane is fitted = %f\n', grid_size);
        fprintf('\tDistance threshold between data point and the plane by RANSAC = %f\n', t);
        fprintf('\tMaximum slope of RANSAC plane with regard to the XoY plane = %f\n', max_slope);
        fprintf('\tCenter of the point cloud (x, y) = [%f, %f]\n', extent_center);

        % divide the XoY extent to grids and fit points in each grid to a plane with RANSAC
        xmin = min(datax); xmax = max(datax);
        ymin = min(datay); ymax = max(datay);
        grid_xsize_left = ceil((extent_center(1) - xmin)/grid_size);
        grid_xsize = ceil((xmax - extent_center(1))/grid_size) + grid_xsize_left;
        grid_ysize_lower = ceil((extent_center(2) - ymin)/grid_size);
        grid_ysize = ceil((ymax - extent_center(2))/grid_size) + grid_ysize_lower;
        grid_cnt = grid_xsize * grid_ysize;

        grid_ix = zeros(npts, 1);
        grid_iy = zeros(npts, 1);
        tmpflag = datax<extent_center(1);
        grid_ix(tmpflag) = ceil((extent_center(1) - datax(tmpflag))/grid_size);
        tmpflag = datax>=extent_center(1);
        grid_ix(tmpflag) = ceil((datax(tmpflag) - extent_center(1))/grid_size) + grid_xsize_left;

        tmpflag = datay<extent_center(2);
        grid_iy(tmpflag) = ceil((extent_center(2) - datay(tmpflag))/grid_size);
        tmpflag = datay>=extent_center(2);
        grid_iy(tmpflag) = ceil((datay(tmpflag) - extent_center(2))/grid_size) + grid_ysize_lower;
        
        grid_idx = (grid_iy-1)*grid_xsize + grid_ix;

        X = ([datax, datay, dataz])';
        grid_gflag = cell(grid_cnt, 1);
        grid_ptsidx = cell(grid_cnt, 1);
        grid_P = cell(grid_cnt, 1);
        parfor i = 1:grid_cnt
            tmpind = find(grid_idx == i);
            [gflag, dist, P] = refineGroundByRansac(X(:, tmpind), t, max_slope);
            grid_ptsidx{i} = tmpind(:);
            grid_gflag{i} = gflag(:);
            grid_P{i} = P;

            % % for debug
            % if length(tmpind)<3
            %     continue;
            % end
            % bins = min(dist):0.05:max(dist);
            % if length(bins) > 3
            %     fig = figure('Visible', 'off');
            %     hist(dist, bins);
            %     saveas(fig, fullfile(GroundPtsPathName, ['dist_hist_', sprintf('%d', i), '.png']));            
            % end
        end

        ground_flag = logical(zeros(npts, 1));
        grid_gflag = cell2mat(grid_gflag);
        grid_ptsidx = cell2mat(grid_ptsidx);
        grid_P = cell2mat(grid_P);
        size_tmp = size(grid_P);
        ground_P = zeros(npts, size_tmp(2));
        ground_flag(grid_ptsidx) = grid_gflag;
        ground_P(grid_ptsidx, :) = grid_P;
        if isempty(ground_extra)
            ground_extra = ground_P;
        else
            ground_extra = [ground_extra, groud_P];
        end
                
        datax = datax(ground_flag);
        datay = datay(ground_flag);
        dataz = dataz(ground_flag);
        line_num = line_num(ground_flag);
        ground_extra = ground_extra(ground_flag, :);
    end


    if refine_single_scan
        fprintf('Refine ground points by removing points above the unscanned area at the center of single terrestrial scans.\n');
        fprintf('\tOrigin of Z axis is assumed at ground level.\n');

        tmpflag = z<1e-3 & z>-1e-3;
        hrange = min(x(tmpflag).^2+y(tmpflag).^2);

        ground_valid_flag = logical(ones(length(datax), 1));

        tmpflag = (datax.^2+datay.^2) < 4*hrange;
        [B, P, newind] = ransacfitplane(([datax(tmpflag), datay(tmpflag), dataz(tmpflag)])', 0.25, 0);

        % fprintf('%f,%f,%f,%f\n', B);
        % tmpx = [0, 1, 2];
        % tmpy = [0, 0, 2];
        % tmpz = (-B(1)*tmpx - B(2)*tmpy - B(4))/B(3);
        % fprintf('%f,%f,%f\n', [tmpx;tmpy;tmpz]);
        % fprintf('%f,%f,%f\n', P);

        tmpflag = datax.^2+datay.^2<=hrange;
        tmpind = find(tmpflag);
        dist = point2planeB(B, ([datax(tmpflag), datay(tmpflag), dataz(tmpflag)])');
        % determine the sign of distance for points above the plane
        test_dist = point2planeB(B, [0;0;100]);
        ground_valid_flag(tmpind(dist*sign(test_dist) > 5e-2)) = false;
        newind = find(ground_valid_flag);

        datax = datax(newind);
        datay = datay(newind);
        dataz = dataz(newind);
        line_num = line_num(newind);
        if ~isempty(ground_extra)
            ground_extra = ground_extra(newind, :);
        end
    end
    if ~ground_extra_flag
        ground_extra = [];
    end

    % newgpfid=fopen(fullfile(GroundPtsPathName, GroundPtsFileName), 'w');
    % fprintf(newgpfid, '%.3f %.3f %.3f\n', ([datax, datay, dataz])');
    % fclose(newgpfid);

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
            if isempty(ground_extra)
                fprintf(nfid, '%s,ground_label\n', header{1}{i});
            else
                size_tmp = size(ground_extra);
                tmpstr = '';
                for ige=1:size_tmp(2)
                    tmpstr = [tmpstr, sprintf(',ground_extra_%d', ige)];
                end
                fprintf(nfid, '%s,ground_label%s\n', header{1}{i}, tmpstr);
            end
        else
            fprintf(nfid, '%s\n', header{1}{i});
        end
    end
    ground_flag = zeros(length(data{1}), 1);
    ground_flag(line_num) = 1;
    ground_flag = logical(ground_flag);
    if ~isempty(ground_extra)
        size_tmp = size(ground_extra);
        tmp = ground_extra;
        ground_extra = zeros(length(data{1}), size_tmp(2));
        ground_extra(line_num, :) = tmp;

        size_tmp = size(ground_extra);
        fmtstr = '%s,%d';
        for ige=1:size_tmp(2)
            fmtstr = [fmtstr, ',%f'];
        end
        fmtstr=[fmtstr, '\n'];
    end

    nrows = length(data{1});
    progress_cnt = round(0.1*nrows);
    fprintf('Writing progress percentage: 0');
    for i=1:nrows
        if ground_flag(i)
            fprintf(fid, '%s\n', data{1}{i});
        end

        if isempty(ground_extra)
            fprintf(nfid, '%s,%d\n', data{1}{i}, ground_flag(i));
        else
            fprintf(nfid, fmtstr, data{1}{i}, ground_flag(i), ground_extra(i, :));
        end

        if mod(i, progress_cnt) == 0
           fprintf('...%.0f', 100*i/nrows);
        end
    end
    fprintf('\n');
    fclose(fid);
    fclose(nfid);

    fprintf('Ground filtering by varying-scale TIN finished!\n');


%------------------------------------------------------------------------
% Function to calculate distances between a plane and a an array of points.
% The plane is defined by a 3x3 matrix, P.  The three columns of P defining
% three points that are within the plane.
function d = point2planeP(P, X)
    
    n = cross(P(:,2)-P(:,1), P(:,3)-P(:,1)); % Plane normal.
    n = n/norm(n);                           % Make it a unit vector.
    
    npts = length(X);
    d = zeros(npts,1);   % d will be an array of distance values.

    % The following loop builds up the dot product between a vector from P(:,1)
    % to every X(:,i) with the unit plane normal.  This will be the
    % perpendicular distance from the plane for each point
    for i=1:3
	d = d + (X(i,:)'-P(i,1))*n(i); 
    end

function d = point2planeB(B, X)
% B, 4x1
% X, 3xNpts
    
    size_X = size(X);
    X_p = [X; ones(1, size_X(2))];
    tmp1 = B' * X_p;
    tmp2 = sqrt(sum(B(1:3).^2));
    d = tmp1/tmp2;


function uX = uniformPointsOnXY(X)
% X, 3xNpts
% uX, 3xnewNpts
    size_X = size(X);
    xmin = min(X(1, :));
    xmax = max(X(1, :));
    ymin = min(X(2, :));
    ymax = max(X(2, :));
    meanpa = (xmax-xmin)*(ymax-ymin)/size_X(2); % mean area per point
    % min_grid_size = (xmax-xmin)/(2^31-1)*10;
    % tmp = (ymax-ymin)/(2^31-1)*10;
    % if min_grid_size > tmp
    %     min_grid_size = tmp   
    % end
    min_grid_size = 1e-3;
    grid_size = sqrt(meanpa);
    if grid_size < min_grid_size
        grid_size = min_grid_size;
    end
    grid_xsize = ceil((xmax-xmin+0.5)/grid_size);
    grid_ysize = ceil((ymax-ymin+0.5)/grid_size);
    grid_ix = ceil((X(1, :) - xmin + 0.5)/grid_size);
    grid_iy = ceil((X(2, :) - ymin + 0.5)/grid_size);
    grid_idx = sub2ind([grid_ysize, grid_xsize], grid_iy, grid_ix);
    grid_idx = grid_idx(:);
    valid_x = accumarray(grid_idx, X(1, :), [], @mean);
    valid_y = accumarray(grid_idx, X(2, :), [], @mean);
    valid_z = accumarray(grid_idx, X(3, :), [], @mean);
    valid_cnt = accumarray(grid_idx, ones(size(X(1, :))));
    tmpflag = valid_cnt>0;
    valid_x = valid_x(tmpflag);
    valid_y = valid_y(tmpflag);
    valid_z = valid_z(tmpflag);
    uX = ([valid_x(:), valid_y(:), valid_z(:)])';


function [ground_flag, dist, post_prob] = refineGroundByRansac(X, t, max_slope)
% X: 3xNpts
% t: scalar, distance threshold in RANSAC
% max_slope: scalar, maximum slope of a plane in degrees
% ground_flag: 1xNpts, boolean vector of whether a point is ground or not

    % Fit a GMM to the distribution of distances between all points to
    % the RANSAC plane to filter above-ground points. Initially
    % assume three components represent negative (below-ground-plane),
    % near-zero (ground-plane) and positive (above-ground-plane)
    % distance
    ncomp0 = 3;

    size_X = size(X);
    ground_flag = logical(zeros(1, size_X(2)));
    dist = zeros(1, size_X(2));
    post_prob = zeros(size_X(2), ncomp0);

    if size_X(2)<3
        fprintf('Number of points less than 3. Refinement by RANSAC plane fit not feasible. All points are labeled non-ground.\n');
        return;
    end
    
    % For TLS, especially single scans, point density varies a lot
    % across range and thus leads higher weight over
    % high-point-density area in the plane fitting which could cause
    % incorrect fitted plane.
    %
    % Here we first decimate the points to achieve a pseudo uniform
    % point density over XoY plane. 
    uX = uniformPointsOnXY(X);
    size_uX = size(uX);
    if size_uX(2)<3
        fprintf('Number of points after uniforming procedure less than 3. Refinement by RANSAC plane fit not feasible. All points are labeled non-ground.\n');
        return;
    end
    [B, P, junk] = ransacfitplane(uX, t, 0);
    % check if the plane has a slope larger than given degree relative to the XoY plane.
    tmpnormal = [0; 0; 1];
    tmp = abs(sum(B(1:3).*tmpnormal))/(sqrt(sum(B(1:3).^2))*sqrt(sum(tmpnormal.^2)));
    if tmp < cos(deg2rad(max_slope))
        % warning(sprintf('Slope of plane with regard to XoY plane is larger than %f deg.\nAll points are labeled non-ground.', max_slope));
        return;
    end
    dist = point2planeB(B, X);
    % determine the sign of distance for points above the plane defined by B
    test_dist = point2planeB(B, [mean(X(1,:));mean(X(2,:));10*abs(max(X(3, :)))]);    
    dist = dist*sign(test_dist);
    dist = dist(:);
    
    % fit a GMM to the distance between all points and the RANSAC plane.
    ncomp = ncomp0;
    notdone = true;
    warning('off', 'all');
    while notdone
        if ncomp < 1 | ncomp >= length(dist)
            % GMM failed and fall back to thresholding method
            warning(sprintf('Gotcha! Distances of points to the fitted plane not able to fit a normal distribution\nFall back to simple thresholding method.'));
            ground_flag(dist<t) = true;
            return;
        end
        try
            options = statset('MaxIter', 1000);
            gmobj = gmdistribution.fit(dist, ncomp, 'Options', options, 'CovType', 'diagonal', 'Replicates', 10);
            if gmobj.Converged
                notdone = false;
            else
                ncomp = ncomp - 1;
            end
        catch ME
            fprintf('%s Rerun GMM fit with one less components.\n', ME.message);
            ncomp = ncomp - 1;
        end
    end
    [idx, junk, P] = cluster(gmobj, dist);
    [sortmu, sortidx] = sort(gmobj.mu);
    sortSigma = gmobj.Sigma(:,:,sortidx);
    [junk, target_idx] = min(abs(sortmu));
    [junk, sortidx] = sort(sortidx);
    % avoid overfiltering ground points due to spurious fitted Gaussians from GMM
    while (sum(sortidx(idx)<=target_idx) < 3) & (target_idx < ncomp)
        target_idx = target_idx + 1;
    end
    ground_flag(sortidx(idx)<=target_idx) = true;

    % post_prob = posterior(gmobj, dist);
    % post_prob = post_prob(:, sortidx);
    % % Avoid overfiltering ground points due to two Gaussians very
    % % close to each other. In this case, posterior prob. of target
    % % ground point could be very close to the posterior prob. of
    % % points in a Gaussian above the currently-found target ground. We
    % % examine the difference of posterior prob. between two close
    % % Gaussians. Then for these above-ground points, even if their
    % % posterior for the target-ground Gaussian is lower than the
    % % above-ground Gaussian but just slightly lower, then we reassign
    % % them as ground points.
    % if target_idx < ncomp
    %     for i=target_idx+1:ncomp
    %         tmpflag = sortidx(idx);
    %         tmp = post_prob(tmpflag, i)./post_prob(tmpflag, target_idx);
    %         tmpflag2 = tmp<2.;
    %         ground_flag(tmpflag2) = true;
    %     end
    % end

    if target_idx == ncomp
       % all the GMM components are on- or below-ground, no
       % above-ground component is found. Further filter out
       % above-ground points by thresholding the likelihood of
       % observed data, distance.
       tmpcdf = normcdf(dist, sortmu(target_idx), sortSigma(:,:,target_idx));
       ground_flag(tmpcdf>0.95) = false;
    end

    post_prob = [post_prob(:, target_idx:ncomp), zeros(size_X(2), ncomp0-ncomp+target_idx-1)];

    warning('on', 'all');