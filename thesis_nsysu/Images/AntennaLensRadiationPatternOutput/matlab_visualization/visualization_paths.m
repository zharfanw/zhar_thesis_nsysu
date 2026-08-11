function paths = visualization_paths()
%VISUALIZATION_PATHS Resolve data and output paths for this MATLAB package.

paths.root = fileparts(mfilename("fullpath"));
paths.data = fullfile(paths.root, "data");
paths.figures = fullfile(paths.root, "figures");
paths.geometryData = fullfile(paths.root, "..", "transmitarray_3d", "data");

if ~isfolder(paths.figures)
    mkdir(paths.figures);
end
end
