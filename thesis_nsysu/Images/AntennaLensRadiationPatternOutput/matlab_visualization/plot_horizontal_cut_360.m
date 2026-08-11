function fig = plot_horizontal_cut_360()
%PLOT_HORIZONTAL_CUT_360 Display the full 360-degree X-Y-plane cut.

paths = visualization_paths();
dataFile = fullfile(paths.data, "horizontal_cut_360_all_patterns.csv");
assert(isfile(dataFile), "Missing data file: %s", dataFile);

data = readtable(dataFile, "TextType", "string");
scenarioTable = unique(data(:, ["scenario", "lens_angle_deg"]), "rows", "stable");
scenarioTable = sortrows(scenarioTable, "lens_angle_deg");
colors = parula(height(scenarioTable));

fprintf("Horizontal-cut data preview:\n");
disp(data(1:min(20, height(data)), :));

fig = figure( ...
    "Name", "Full 360 Degree Horizontal Cut", ...
    "Color", "white", ...
    "Position", [120, 70, 950, 850]);
polarAxis = polaraxes(fig);
hold(polarAxis, "on");

for index = 1:height(scenarioTable)
    scenarioName = string(scenarioTable.scenario(index));
    selection = string(data.scenario) == scenarioName;
    scenarioData = sortrows(data(selection, :), "horizontal_angle_deg");
    polarplot( ...
        polarAxis, ...
        deg2rad(scenarioData.horizontal_angle_deg), ...
        scenarioData.gain_db, ...
        "LineWidth", 1.4, ...
        "Color", colors(index, :), ...
        "DisplayName", scenarioName);
end

polarAxis.ThetaZeroLocation = "right";
polarAxis.ThetaDir = "counterclockwise";
polarAxis.ThetaTick = 0:45:315;
polarAxis.ThetaTickLabel = {"+X", "45°", "+Y", "135°", "-X", "225°", "-Y", "315°"};
polarAxis.FontSize = 10;
title(polarAxis, "Full 360° Horizontal Cut (X-Y Plane) — All Lens Angles");
legend(polarAxis, "Location", "eastoutside", "Interpreter", "none");

outputFile = fullfile(paths.figures, "matlab_horizontal_cut_360_all_patterns.png");
exportgraphics(fig, outputFile, "Resolution", 220);
fprintf("Saved: %s\n", outputFile);
end
