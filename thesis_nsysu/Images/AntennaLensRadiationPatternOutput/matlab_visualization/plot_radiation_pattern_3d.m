function fig = plot_radiation_pattern_3d()
%PLOT_RADIATION_PATTERN_3D Display normalized 3D radiation surfaces.

paths = visualization_paths();
dataFile = fullfile(paths.data, "radiation_pattern_3d_all_patterns.csv");
assert(isfile(dataFile), "Missing data file: %s", dataFile);

data = readtable(dataFile, "TextType", "string");
scenarioTable = unique(data(:, ["scenario", "lens_angle_deg"]), "rows", "stable");
scenarioTable = sortrows(scenarioTable, "lens_angle_deg");

fprintf("3D radiation-pattern data preview:\n");
disp(data(1:min(20, height(data)), :));

fig = figure( ...
    "Name", "3D Radiation Patterns", ...
    "Color", "white", ...
    "Position", [30, 30, 1550, 900]);
layout = tiledlayout(fig, 2, 3, "TileSpacing", "compact", "Padding", "compact");
title(layout, "Normalized 3D Radiation Patterns (40 dB Dynamic Range)");

for index = 1:height(scenarioTable)
    scenarioName = string(scenarioTable.scenario(index));
    selection = string(data.scenario) == scenarioName;
    scenarioData = data(selection, :);

    thetaValues = unique(scenarioData.theta_deg, "sorted");
    phiValues = unique(scenarioData.phi_deg, "sorted");
    thetaCount = numel(thetaValues);
    phiCount = numel(phiValues);
    assert(height(scenarioData) == thetaCount * phiCount, ...
        "Incomplete spherical grid for %s", scenarioName);

    xGrid = reshape(scenarioData.x, [phiCount, thetaCount]).';
    yGrid = reshape(scenarioData.y, [phiCount, thetaCount]).';
    zGrid = reshape(scenarioData.z, [phiCount, thetaCount]).';
    gainGrid = reshape(scenarioData.gain_db, [phiCount, thetaCount]).';

    axisHandle = nexttile(layout);
    surf( ...
        axisHandle, xGrid, yGrid, zGrid, gainGrid, ...
        "EdgeColor", "none", ...
        "FaceColor", "interp");
    axis(axisHandle, "equal");
    axis(axisHandle, "tight");
    grid(axisHandle, "on");
    view(axisHandle, 40, 28);
    xlabel(axisHandle, "X");
    ylabel(axisHandle, "Y");
    zlabel(axisHandle, "Z");
    title(axisHandle, scenarioName, "Interpreter", "none");
    colorbar(axisHandle);
    clim(axisHandle, [max(gainGrid, [], "all") - 40.0, max(gainGrid, [], "all")]);
end

colormap(fig, parula(256));
outputFile = fullfile(paths.figures, "matlab_radiation_pattern_3d_all_patterns.png");
exportgraphics(fig, outputFile, "Resolution", 220);
fprintf("Saved: %s\n", outputFile);
end
