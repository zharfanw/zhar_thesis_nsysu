%% Generate all figures for the six-scenario comparison
% Linear, half-circle, and full-circle trajectories; lens vs without lens.
% Run this script from any working directory. All paths are resolved relative
% to the location of this file.

clear; close all; clc;

scriptDir = fileparts(mfilename('fullpath'));
dataDir = fullfile(scriptDir, 'data');
outputDir = fullfile(scriptDir, 'matlab_figures');
if ~exist(outputDir, 'dir')
    mkdir(outputDir);
end

fprintf('Reading comparison data from:\n  %s\n', dataDir);

scenarioKeys = ["linear_lens", "linear_wolens", ...
                "half_lens", "half_wolens", ...
                "full_lens", "full_wolens"];
scenarioTitles = ["Linear - lens", "Linear - without lens", ...
                  "Half-circle - lens", "Half-circle - without lens", ...
                  "Full-circle - lens", "Full-circle - without lens"];

lensColor = [0.145, 0.388, 0.922];
noLensColor = [0.918, 0.345, 0.047];

%% Figure 1: antenna positions and trajectory geometry
fig = figure('Color', 'w', 'Position', [70 40 1250 1450]);
tiledlayout(3, 2, 'TileSpacing', 'compact', 'Padding', 'compact');

for k = 1:numel(scenarioKeys)
    key = scenarioKeys(k);
    trajectoryType = extractBefore(key, "_");
    trajectoryData = readtable(fullfile(dataDir, "trajectory_" + key + ".csv"));
    rxData = readtable(fullfile(dataDir, "rx_" + key + ".csv"));

    [txX, txY] = trajectoryCenters(trajectoryData, trajectoryType);

    ax = nexttile;
    plot(ax, txX, txY, '-o', 'Color', [0.05 0.45 0.72], ...
        'LineWidth', 1.5, 'MarkerSize', 3, 'DisplayName', 'TX center');
    hold(ax, 'on');
    scatter(ax, rxData.x_m, rxData.y_m, 48, [0.98 0.78 0.08], 's', ...
        'filled', 'MarkerEdgeColor', 'k', 'DisplayName', '9 RX');
    hold(ax, 'off');
    title(ax, scenarioTitles(k), 'Interpreter', 'none');
    xlabel(ax, 'X (m)'); ylabel(ax, 'Y (m)');
    xlim(ax, [-10.5 10.5]); ylim(ax, [-10.5 10.5]);
    axis(ax, 'equal'); grid(ax, 'on'); box(ax, 'on');
    legend(ax, 'Location', 'best');
end
sgtitle('Antenna Positions and Trajectory Geometry');
exportFigure(fig, outputDir, '01_geometry_six_scenarios');

%% Figures 2-4: all evaluation parameters grouped by identical trajectory
makeEvaluationDashboard(dataDir, outputDir, "linear", ...
    'Linear trajectory: lens vs without lens', lensColor, noLensColor);
makeEvaluationDashboard(dataDir, outputDir, "half", ...
    'Half-circular trajectory: lens vs without lens', lensColor, noLensColor);
makeEvaluationDashboard(dataDir, outputDir, "full", ...
    'Full-circular trajectory: lens vs without lens', lensColor, noLensColor);

%% Figure 5: aggregate comparison across trajectory types
summaryData = readtable(fullfile(dataDir, 'comparison_summary.csv'));
fig = figure('Color', 'w', 'Position', [70 70 1450 820]);
tiledlayout(2, 3, 'TileSpacing', 'compact', 'Padding', 'compact');

metricNames = ["magnitude_median_db", "snr_median_db", ...
               "capacity_median_bits_s_hz", "pooled_decorrelation", ...
               "median_decorrelation", "condition_number_median_db"];
metricTitles = ["Median magnitude (dB)", "Median SNR (dB)", ...
                "Median capacity (bit/s/Hz)", "Pooled decorrelation", ...
                "Median decorrelation", "Median condition number (dB)"];
trajectoryNames = ["Linear", "Half-circle", "Full-circle"];
trajectoryKeys = ["linear", "half", "full"];

for m = 1:numel(metricNames)
    ax = nexttile;
    lensValues = zeros(1, 3);
    noLensValues = zeros(1, 3);
    for t = 1:3
        lensRow = strcmp(string(summaryData.scenario), trajectoryKeys(t) + "_lens");
        noLensRow = strcmp(string(summaryData.scenario), trajectoryKeys(t) + "_wolens");
        lensValues(t) = summaryData{lensRow, metricNames(m)};
        noLensValues(t) = summaryData{noLensRow, metricNames(m)};
    end
    plot(ax, lensValues, 1:3, '-o', 'Color', lensColor, ...
        'LineWidth', 1.6, 'MarkerSize', 7, 'DisplayName', 'Lens');
    hold(ax, 'on');
    plot(ax, noLensValues, 1:3, '--s', 'Color', noLensColor, ...
        'LineWidth', 1.6, 'MarkerSize', 7, 'DisplayName', 'Without lens');
    hold(ax, 'off');
    yticks(ax, 1:3); yticklabels(ax, trajectoryNames);
    ylim(ax, [0.7 3.3]); title(ax, metricTitles(m));
    grid(ax, 'on'); box(ax, 'on'); legend(ax, 'Location', 'best');
end
sgtitle('Aggregate Metric Comparison Across Trajectory Types');
exportFigure(fig, outputDir, '05_aggregate_comparison');

fprintf('\nFinished. MATLAB figures were saved to:\n  %s\n', outputDir);

%% Local functions
function makeEvaluationDashboard(dataDir, outputDir, trajectoryType, ...
    mainTitle, lensColor, noLensColor)

    lensKey = trajectoryType + "_lens";
    noLensKey = trajectoryType + "_wolens";

    lens = loadScenarioData(dataDir, lensKey);
    noLens = loadScenarioData(dataDir, noLensKey);
    summaryData = readtable(fullfile(dataDir, 'comparison_summary.csv'));

    lensRow = strcmp(string(summaryData.scenario), lensKey);
    noLensRow = strcmp(string(summaryData.scenario), noLensKey);
    lensMagnitude = summaryData.magnitude_median_db(lensRow);
    noLensMagnitude = summaryData.magnitude_median_db(noLensRow);

    fig = figure('Color', 'w', 'Position', [40 30 1650 1150]);
    tiledlayout(3, 3, 'TileSpacing', 'compact', 'Padding', 'compact');

    plotMetric(nexttile, lens.trajectory, noLens.trajectory, ...
        'mean_snr_db', 'Mean SNR - 9 RX', 'dB', false, lensColor, noLensColor);
    plotMetric(nexttile, lens.trajectory, noLens.trajectory, ...
        'capacity_bits_s_hz', 'Mean channel capacity - 9 RX', ...
        'bit/s/Hz', false, lensColor, noLensColor);
    plotMetric(nexttile, lens.pooled, noLens.pooled, ...
        'mean_spatial_decorrelation', 'Pooled spatial decorrelation', ...
        'Coefficient', false, lensColor, noLensColor, [0 1]);
    plotMetric(nexttile, lens.median, noLens.median, ...
        'median_pair_decorrelation', 'Median-block spatial decorrelation', ...
        'Coefficient', false, lensColor, noLensColor, [0 1]);
    plotMetric(nexttile, lens.raw, noLens.raw, ...
        'mean_raw_cross_correlation', 'Raw cross-correlation', ...
        'Raw power', true, lensColor, noLensColor);
    plotMetric(nexttile, lens.raw, noLens.raw, ...
        'mean_raw_difference_power', 'Raw difference power', ...
        'Raw power', true, lensColor, noLensColor);
    plotMetric(nexttile, lens.mimo, noLens.mimo, ...
        'cond_median_db', 'Median condition number', ...
        'dB', false, lensColor, noLensColor);
    plotMetric(nexttile, lens.mimo, noLens.mimo, ...
        'erank_median', 'Median effective rank', ...
        'Rank', false, lensColor, noLensColor);
    plotMetric(nexttile, lens.mimo, noLens.mimo, ...
        'capacity_10db', 'MIMO capacity @ 10 dB', ...
        'bit/s/Hz', false, lensColor, noLensColor);

    sgtitle(sprintf('%s\nMedian channel magnitude: lens %.2f dB | without lens %.2f dB', ...
        mainTitle, lensMagnitude, noLensMagnitude));
    exportFigure(fig, outputDir, "02_" + trajectoryType + "_all_parameters");
end

function data = loadScenarioData(dataDir, key)
    data.trajectory = readtable(fullfile(dataDir, "trajectory_" + key + ".csv"));
    data.trajectory = groupsummary(data.trajectory, 'distance_along_m', 'mean', ...
        {'mean_snr_db', 'capacity_bits_s_hz'});
    data.trajectory.Properties.VariableNames{strcmp(data.trajectory.Properties.VariableNames, ...
        'mean_mean_snr_db')} = 'mean_snr_db';
    data.trajectory.Properties.VariableNames{strcmp(data.trajectory.Properties.VariableNames, ...
        'mean_capacity_bits_s_hz')} = 'capacity_bits_s_hz';
    data.pooled = readtable(fullfile(dataDir, "pooled_" + key + ".csv"));
    data.median = readtable(fullfile(dataDir, "median_" + key + ".csv"));
    data.raw = readtable(fullfile(dataDir, "raw_" + key + ".csv"));
    data.mimo = readtable(fullfile(dataDir, "mimo_" + key + ".csv"));
end

function plotMetric(ax, lensTable, noLensTable, variableName, plotTitle, ...
    yLabelText, useLogScale, lensColor, noLensColor, yLimits)
    plot(ax, lensTable.distance_along_m, lensTable.(variableName), '-o', ...
        'Color', lensColor, 'LineWidth', 1.5, 'MarkerSize', 4, ...
        'MarkerIndices', 1:3:height(lensTable), 'DisplayName', 'Lens');
    hold(ax, 'on');
    plot(ax, noLensTable.distance_along_m, noLensTable.(variableName), '--s', ...
        'Color', noLensColor, 'LineWidth', 1.5, 'MarkerSize', 4, ...
        'MarkerIndices', 1:3:height(noLensTable), 'DisplayName', 'Without lens');
    hold(ax, 'off');
    if useLogScale
        set(ax, 'YScale', 'log');
    end
    if nargin >= 10 && ~isempty(yLimits)
        ylim(ax, yLimits);
    end
    title(ax, plotTitle); xlabel(ax, 'Distance along trajectory (m)');
    ylabel(ax, yLabelText); grid(ax, 'on'); box(ax, 'on');
    legend(ax, 'Location', 'best');
end

function [x, y] = trajectoryCenters(trajectoryData, trajectoryType)
    if trajectoryType == "linear"
        [~, firstRows] = unique(trajectoryData.waypoint, 'stable');
        x = trajectoryData.tx_center_x_m(firstRows);
        y = trajectoryData.tx_center_y_m(firstRows);
    else
        numberOfWaypoints = numel(unique(trajectoryData.waypoint));
        if trajectoryType == "half"
            theta = linspace(-pi/2, pi/2, numberOfWaypoints);
        else
            theta = linspace(0, 2*pi, numberOfWaypoints);
        end
        x = 9*cos(theta(:));
        y = 9*sin(theta(:));
    end
end

function exportFigure(fig, outputDir, baseName)
    drawnow;
    savefig(fig, fullfile(outputDir, baseName + ".fig"));
    exportgraphics(fig, fullfile(outputDir, baseName + ".png"), ...
        'Resolution', 180);
end
