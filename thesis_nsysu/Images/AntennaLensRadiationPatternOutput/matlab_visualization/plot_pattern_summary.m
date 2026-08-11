function fig = plot_pattern_summary()
%PLOT_PATTERN_SUMMARY Display gain, directivity, efficiency, and peak angles.

paths = visualization_paths();
dataFile = fullfile(paths.data, "pattern_summary.csv");
assert(isfile(dataFile), "Missing data file: %s", dataFile);

data = readtable(dataFile, "TextType", "string");
data = sortrows(data, "lens_angle_deg");

fprintf("Pattern summary data:\n");
disp(data);

fig = figure( ...
    "Name", "Antenna Pattern Summary", ...
    "Color", "white", ...
    "Position", [80, 80, 1250, 760]);
layout = tiledlayout(fig, 2, 2, "TileSpacing", "compact", "Padding", "compact");
title(layout, "RX Lens Radiation-Pattern Summary");

nexttile;
plot(data.lens_angle_deg, data.directivity_db, "-o", "LineWidth", 1.6);
hold on;
plot(data.lens_angle_deg, data.gain_db, "-s", "LineWidth", 1.6);
grid on;
xlabel("Lens angle (deg)");
ylabel("Level (dB)");
title("Directivity and gain");
legend("Directivity", "Gain", "Location", "best");

nexttile;
bar(data.lens_angle_deg, data.efficiency_pct, 0.65);
grid on;
xlabel("Lens angle (deg)");
ylabel("Efficiency (%)");
title("Radiation efficiency");

nexttile;
plot(data.lens_angle_deg, data.theta_peak_deg, "-o", "LineWidth", 1.6);
hold on;
plot(data.lens_angle_deg, data.phi_peak_deg, "-s", "LineWidth", 1.6);
grid on;
xlabel("Lens angle (deg)");
ylabel("Peak direction (deg)");
title("Local peak direction");
legend("\theta_{peak}", "\phi_{peak}", "Location", "best");

nexttile;
bar(categorical(data.name), data.gain_db);
grid on;
ylabel("Gain (dB)");
title("Gain by scenario");
xtickangle(35);

outputFile = fullfile(paths.figures, "matlab_pattern_summary.png");
exportgraphics(fig, outputFile, "Resolution", 220);
fprintf("Saved: %s\n", outputFile);
end
