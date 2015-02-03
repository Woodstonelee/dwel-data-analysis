function [canopyprofile, meanangle, avd] = LM_pgap2profile(midzeniths,heights,pgapz)
% midzeniths: deg
% heights: meter
    kthetal = -log(pgapz);
    xtheta = 2/pi*tan(midzeniths/180*pi);
    AIv = ones(length(heights), 1);
    AIh = ones(length(heights), 1);
    for hi=1:length(heights)
        p = polyfit(reshape(xtheta, length(xtheta), 1), kthetal(:,hi), 1);
        AIv(hi) = p(1);
        AIh(hi) = p(2);
    end
    canopyprofile = AIv + AIh;
    meanangle = 90 - atan2(AIv, AIh);
    avd = diff(canopyprofile)./diff(heights);
end