function  OutCutH = mexFilterVarScaleTIN(InPtsPathName, InPtsFileName, ...
					  GroundPtsPathName, GroundPtsFileName, ...
					  scale, door, ...
					  xlim, ylim, ...
					  CutH, CalCutH, ...
					  NonGroundPtsPathName, NonGroundPtsFileName, ...
                      EachScalePathName)

% mexFilterVarScaleTIN: 
% Filter the terrestrial laser points with var-scale TIN and then give the
% ground points. 
% 
% SYNTAX: 
%   mexFilterVarScaleTIN(InPtsPathName, InPtsFileName, ...
% 					  GroundPtsPathName, GroundPtsFileName, ...
% 					  scale, door, ...
% 					  xlim, ylim, ...
% 					  CutH, CalCutH, ...
% 					  NonGroundPtsPathName, NonGroundPtsFileName)
%    
%  REQUIRED INPUT: 
% 	InPtsPathName, InPtsFileName: both strings, the path and file name of the input point clouds.
% 		Format: no header, in each line: x y z
% 	GroundPtsPathName, GroundPtsFileName: both strings, the path and file anme of the output ground points.
% 		Format: no header, in each line: x y z
% 	scale: N-length vector, the cell size at each scale, N is the number of scales.
% 	door: N-length vector, the distance threshold used to select ground points at each scale, N is the number of scales.
% 	xlim, ylim: both two-length vectors, the extent of x and y in the rasterization.
% 	CutH: scalar, the cut height used to exclude non-ground points. If it is designated, it will be used. If it is empty or NaN, CalCutH must be given to determine the CutH.
%  OPTIONAL INPUT:
% 	CalCutH: two-length vector, [ThicknessZ, Coefficient], ThicknessZ is used to stratify the points into layers across the Z axis. Coefficient is used to determine the CutH with the point distribution from all the layers.
% 	NonGroundPtsPathName, NonGroundPtsFileName: both strings, the path and file name of the output non-ground points. If you will not output these points, leave the two strings as empty([]).
% 		Format: no header, in each line: x y z
%   EachScalePathName: the path of directory for the files of remaining points in each iterations.
% 
%  REQUIRED OUTPUT:
%   Ground points are output in the files with the
%   given names of [GroundPtsPathName, '\', GroundPtsFileName] and
%  OPTIONAL OUTPUT: 
%   non-ground points are output in the files with the given name of
%   [NonGroundPtsPathName, '\', NonGroundPtsFileName].
%   OutCutH: the cut height used in the filtering, either equaling to the
%   given CutH or calculated with the input argument CalCutH.
% 
%  REQUIRED ROUTINES:
%   None.

end