function fig = plot_yz_cut_360()
%PLOT_YZ_CUT_360 Display the full 360-degree Y-Z-plane cut.

paths = visualization_paths();
dataFile = fullfile(paths.data, "yz_cut_360_all_patterns.csv");
assert(isfile(dataFile), "Missing data file: %s", dataFile);

data = readtable(dataFile, "TextType", "string");
scenarioTable = unique(data(:, ["scenario", "lens_angle_deg"]), "rows", "stable");
scenarioTable = sortrows(scenarioTable, "lens_angle_deg");
colors = parula(height(scenarioTable));

fprintf("Y-Z-cut data preview:\n");
disp(data(1:min(20, height(data)), :));

fig = figure( ...
    "Name", "Full 360 Degree Y-Z Cut", ...
    "Color", "white", ...
    "Position", [140, 80, 950, 850]);
polarAxis = polaraxes(fig);
hold(polarAxis, "on");

for index = 1:height(scenarioTable)
    scenarioName = string(scenarioTable.scenario(index));
    selection = string(data.scenario) == scenarioName;
    scenarioData = sortrows(data(selection, :), "yz_angle_deg");
    polarplot( ...
        polarAxis, ...
        deg2rad(scenarioData.yz_angle_deg), ...
        scenarioData.gain_db, ...
        "LineWidth", 1.4, ...
        "Color", colors(index, :), ...
        "DisplayName", scenarioName);
end

polarAxis.ThetaZeroLocation = "top";
polarAxis.ThetaDir = "clockwise";
polarAxis.ThetaTick = 0:45:315;
polarAxis.ThetaTickLabel = {"+Z", "45°", "+Y", "135°", "-Z", "225°", "-Y", "315°"};
polarAxis.FontSize = 10;
title(polarAxis, "Full 360° Y-Z Plane Cut — All Lens Angles");
legend(polarAxis, "Location", "eastoutside", "Interpreter", "none");

outputFile = fullfile(paths.figures, "matlab_yz_cut_360_all_patterns.png");
exportgraphics(fig, outputFile, "Resolution", 220);
fprintf("Saved: %s\n", outputFile);
end
