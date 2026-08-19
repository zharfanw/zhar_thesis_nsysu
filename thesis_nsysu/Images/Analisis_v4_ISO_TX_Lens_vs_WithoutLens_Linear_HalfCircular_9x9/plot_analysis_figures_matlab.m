%% plot_analysis_figures_matlab.m
% Plot ulang analisis Lens vs Without Lens untuk trajectory Linear dan
% Half-Circular menggunakan data CSV yang sudah diekstrak dari notebook.
%
% Perilaku default:
%   1. Tidak menjalankan ulang simulasi Sionna RT.
%   2. MENAMPILKAN delapan figure sebagai window MATLAB (Visible = on).
%   3. Menyimpan setiap figure sebagai PNG dan MATLAB .fig.
%   4. Tidak menutup window figure setelah penyimpanan.
%
% Jalankan dari folder mana pun:
%   run('Analisis_v4_ISO_TX_Lens_vs_WithoutLens_Linear_HalfCircular_9x9/plot_analysis_figures_matlab.m')
%
% Memerlukan MATLAB R2019b atau lebih baru (tiledlayout/exportgraphics).

clearvars;
clc;

analysisDir = fileparts(mfilename('fullpath'));
dataDir = fullfile(analysisDir, 'data');
outputDir = fullfile(analysisDir, 'figures_matlab');

if ~isfolder(dataDir)
    error('Folder data tidak ditemukan: %s', dataDir);
end
if ~isfolder(outputDir)
    mkdir(outputDir);
end

set(groot, 'defaultFigureVisible', 'on');

trajectories = ["Linear", "Half-Circular"];
systems = ["Without Lens", "Lens"];
systemLabels = {'Without Lens', 'Lens'};
colors = [31, 90, 133; 216, 145, 38] / 255;
lineStyles = {'-', '--'};
markers = {'o', 's'};
surfaceColor = [1, 1, 1];
gridColor = [217, 221, 227] / 255;
inkColor = [48, 52, 59] / 255;

set(groot, 'defaultAxesFontName', 'Arial');
set(groot, 'defaultAxesFontSize', 10);
set(groot, 'defaultAxesXGrid', 'on');
set(groot, 'defaultAxesYGrid', 'on');
set(groot, 'defaultAxesGridColor', gridColor);
set(groot, 'defaultAxesColor', surfaceColor);
set(groot, 'defaultAxesXColor', inkColor);
set(groot, 'defaultAxesYColor', inkColor);
set(groot, 'defaultTextInterpreter', 'none');
set(groot, 'defaultLegendInterpreter', 'none');

%% Load data hasil analisis
summary = readAnalysisCsv(fullfile(dataDir, 'comparison_summary.csv'));
rxConfig = readAnalysisCsv(fullfile(dataDir, 'rx_configurations_combined.csv'));
staticRx = readAnalysisCsv(fullfile(dataDir, 'static_summary_combined.csv'));
waypoint = readAnalysisCsv(fullfile(dataDir, 'waypoint_samples_combined.csv'));
trajectoryMimo = readAnalysisCsv(fullfile(dataDir, 'trajectory_mimo_combined.csv'));
spatialPooled = readAnalysisCsv(fullfile(dataDir, 'spatial_pooled_combined.csv'));
spatialMedian = readAnalysisCsv(fullfile(dataDir, 'spatial_median_combined.csv'));
spatialRaw = readAnalysisCsv(fullfile(dataDir, 'spatial_raw_combined.csv'));

validateInputs(summary, waypoint, trajectoryMimo, spatialPooled, ...
    spatialMedian, trajectories, systems);

%% Figure 1 - geometri trajectory dan array
f1 = newVisibleFigure('01 - Trajectory and array geometry', ...
    [30, 35, 1500, 900], surfaceColor);
t1 = tiledlayout(f1, 2, 2, 'TileSpacing', 'loose', 'Padding', 'compact');

for trajectoryIndex = 1:numel(trajectories)
    trajectoryName = trajectories(trajectoryIndex);
    ax = nexttile(t1);
    pathRows = textMask(waypoint, 'trajectory', trajectoryName) & ...
        textMask(waypoint, 'system', "Lens");
    path = sortrows(waypoint(pathRows, :), 'waypoint');
    [~, uniqueRows] = unique(path.waypoint, 'stable');
    path = path(uniqueRows, :);

    plot(ax, path.tx_center_x_m, path.tx_center_y_m, '-o', ...
        'Color', [58, 111, 79] / 255, 'LineWidth', 2, 'MarkerSize', 4, ...
        'DisplayName', 'TX array center');
    hold(ax, 'on');
    for systemIndex = 1:numel(systems)
        rows = textMask(rxConfig, 'trajectory', trajectoryName) & ...
            textMask(rxConfig, 'system', systems(systemIndex));
        block = rxConfig(rows, :);
        scatter(ax, block.rx_x_m, block.rx_y_m, 45, ...
            'Marker', markers{systemIndex}, ...
            'MarkerEdgeColor', colors(systemIndex, :), ...
            'MarkerFaceColor', colors(systemIndex, :), ...
            'DisplayName', sprintf('9 RX - %s', systemLabels{systemIndex}));
    end
    scatter(ax, path.tx_center_x_m(1), path.tx_center_y_m(1), 85, '^', ...
        'filled', 'MarkerFaceColor', colors(2, :), 'DisplayName', 'Start');
    scatter(ax, path.tx_center_x_m(end), path.tx_center_y_m(end), 85, 'x', ...
        'LineWidth', 2.4, 'MarkerEdgeColor', [139, 71, 113] / 255, ...
        'DisplayName', 'End');
    hold(ax, 'off');
    axis(ax, 'equal');
    xlim(ax, [-10, 10]);
    ylim(ax, [-10, 10]);
    xlabel(ax, 'X (m)');
    ylabel(ax, 'Y (m)');
    title(ax, sprintf('%s: top view', trajectoryName));
    legend(ax, 'Location', 'best', 'FontSize', 8);
end

% TX array identik pada semua skenario: 9 elemen ISO, spacing 0.45 m.
txOffsetXmm = zeros(9, 1);
txOffsetYmm = (-1.8:0.45:1.8)' * 1000;
for systemIndex = 1:numel(systems)
    ax = nexttile(t1);
    rows = textMask(rxConfig, 'trajectory', "Linear") & ...
        textMask(rxConfig, 'system', systems(systemIndex));
    block = sortrows(rxConfig(rows, :), 'rx_config_index');
    rxOffsetXmm = (block.rx_x_m - mean(block.rx_x_m)) * 1000;
    rxOffsetYmm = (block.rx_y_m - mean(block.rx_y_m)) * 1000;

    scatter(ax, txOffsetXmm, txOffsetYmm, 60, '^', 'filled', ...
        'MarkerFaceColor', [58, 111, 79] / 255, 'DisplayName', '9 TX ISO');
    hold(ax, 'on');
    scatter(ax, rxOffsetXmm, rxOffsetYmm, 55, markers{systemIndex}, ...
        'MarkerEdgeColor', colors(systemIndex, :), ...
        'MarkerFaceColor', colors(systemIndex, :), 'DisplayName', '9 RX');
    xline(ax, 0, '-', 'Color', inkColor, 'HandleVisibility', 'off');
    yline(ax, 0, '-', 'Color', inkColor, 'HandleVisibility', 'off');
    hold(ax, 'off');
    axis(ax, 'equal');
    xlabel(ax, 'X offset from centroid (mm)');
    ylabel(ax, 'Y offset from centroid (mm)');
    title(ax, sprintf('Local array geometry: %s', systems(systemIndex)));
    legend(ax, 'Location', 'best', 'FontSize', 8);
end
title(t1, {'Trajectory and array geometry: 9 ISO TX x 9 RX', ...
    'TX waypoints are identical; RX cluster designs differ between the two systems'}, ...
    'FontSize', 14, 'FontWeight', 'bold');
saveDisplayedFigure(f1, outputDir, '01_geometry_and_arrays_matlab');

%% Figure 2 - snapshot statis per konfigurasi RX
f2 = newVisibleFigure('02 - Static RX snapshot', ...
    [45, 70, 1550, 520], surfaceColor);
t2 = tiledlayout(f2, 1, 3, 'TileSpacing', 'loose', 'Padding', 'compact');
metricColumns = {'combined_gain_db', 'mean_|rho|_offdiag', ...
    'capacity_10dB_bits/s/Hz'};
metricLabels = {'Combined gain (dB)', 'Mean |rho| off-diagonal', ...
    'Capacity (bit/s/Hz)'};
metricTitles = {'Combined gain: 9 TX', 'TX-branch correlation', ...
    'Normalized capacity @ 10 dB'};

for panel = 1:3
    ax = nexttile(t2);
    values = nan(9, 2);
    for systemIndex = 1:numel(systems)
        rows = textMask(staticRx, 'trajectory', "Linear") & ...
            textMask(staticRx, 'system', systems(systemIndex));
        block = sortrows(staticRx(rows, :), 'rx_config_index');
        values(:, systemIndex) = tableColumn(block, metricColumns{panel});
    end
    groupedBars(ax, values, 0:8, systemLabels, colors, '%.2f');
    if panel == 1
        legend(ax, systemLabels, 'Location', 'northwest', 'FontSize', 8);
    else
        legend(ax, 'off');
    end
    xlabel(ax, 'RX configuration index');
    ylabel(ax, metricLabels{panel});
    title(ax, metricTitles{panel});
end
title(t2, {'Section 9 snapshot at a static TX position', ...
    'Matching indices are ordinal design pairs, not co-located elements'}, ...
    'FontSize', 14, 'FontWeight', 'bold');
saveDisplayedFigure(f2, outputDir, '02_static_rx_scenario_comparison_matlab');

%% Figure 3 - MIMO snapshot statis
f3 = newVisibleFigure('03 - MIMO statis', ...
    [65, 100, 1550, 500], surfaceColor);
t3 = tiledlayout(f3, 1, 4, 'TileSpacing', 'loose', 'Padding', 'compact');
staticMetrics = {'static_mimo_condition_db', 'static_mimo_effective_rank', ...
    'static_mimo_capacity_10db', 'static_rx_correlation_mean'};
staticTitles = {'Conditioning', 'Effective rank', ...
    'MIMO capacity @ 10 dB', 'RX correlation'};
staticLabels = {'Condition number (dB)', 'Effective rank (/9)', ...
    'Capacity (bit/s/Hz)', 'Mean |rho| off-diagonal'};

for panel = 1:4
    ax = nexttile(t3);
    values = nan(2, 1);
    for systemIndex = 1:numel(systems)
        rows = textMask(summary, 'trajectory', "Linear") & ...
            textMask(summary, 'system', systems(systemIndex));
        values(systemIndex) = tableColumn(summary(rows, :), staticMetrics{panel});
    end
    categoricalBars(ax, values, systemLabels, colors, '%.2f');
    ylabel(ax, staticLabels{panel});
    title(ax, staticTitles{panel});
end
title(t3, {'Synthetic/combined 9x9 MIMO at the static snapshot', ...
    'Constructed by combining nine sequential 9x1 simulations'}, ...
    'FontSize', 14, 'FontWeight', 'bold');
saveDisplayedFigure(f3, outputDir, '03_static_mimo_comparison_matlab');

%% Figure 4 - SNR dan kapasitas sepanjang trajectory
f4 = newVisibleFigure('04 - Channel along trajectory', ...
    [85, 45, 1500, 880], surfaceColor);
t4 = tiledlayout(f4, 2, 2, 'TileSpacing', 'loose', 'Padding', 'compact');
channelColumns = {'snr_db_log_rounded', 'capacity_bits_s_hz_log_rounded'};
channelTitles = {'SNR', 'Capacity'};
channelLabels = {'Mean SNR across 9 RX (dB)', ...
    'Mean capacity across 9 RX (bit/s/Hz)'};

for trajectoryIndex = 1:numel(trajectories)
    for metricIndex = 1:2
        ax = nexttile(t4, (trajectoryIndex - 1) * 2 + metricIndex);
        hold(ax, 'on');
        lineHandles = gobjects(2, 1);
        for systemIndex = 1:numel(systems)
            rows = textMask(waypoint, 'trajectory', trajectories(trajectoryIndex)) & ...
                textMask(waypoint, 'system', systems(systemIndex));
            [x, meanValue, minValue, maxValue] = aggregateByDistance( ...
                waypoint(rows, :), channelColumns{metricIndex});
            fill(ax, [x; flipud(x)], [minValue; flipud(maxValue)], ...
                colors(systemIndex, :), 'FaceAlpha', 0.09, ...
                'EdgeColor', 'none', 'HandleVisibility', 'off');
            lineHandles(systemIndex) = plot(ax, x, meanValue, ...
                'Color', colors(systemIndex, :), ...
                'LineStyle', lineStyles{systemIndex}, ...
                'Marker', markers{systemIndex}, 'MarkerSize', 4, ...
                'LineWidth', 2, 'DisplayName', systemLabels{systemIndex});
        end
        if metricIndex == 2
            yline(ax, 1, '-', 'Outage threshold', 'Color', inkColor, ...
                'LineWidth', 1, 'HandleVisibility', 'off');
        end
        hold(ax, 'off');
        xlabel(ax, 'Distance along trajectory (m)');
        ylabel(ax, channelLabels{metricIndex});
        title(ax, sprintf('%s: %s', trajectories(trajectoryIndex), ...
            channelTitles{metricIndex}));
        legend(ax, lineHandles, systemLabels, 'Location', 'best');
    end
end
title(t4, {'Channel performance along the trajectory', ...
    'Lines = mean across 9 RX; bands = minimum-to-maximum RX range'}, ...
    'FontSize', 14, 'FontWeight', 'bold');
saveDisplayedFigure(f4, outputDir, '04_channel_metrics_along_trajectory_matlab');

%% Figure 5 - MIMO sepanjang trajectory
f5 = newVisibleFigure('05 - MIMO along trajectory', ...
    [105, 30, 1450, 940], surfaceColor);
t5 = tiledlayout(f5, 3, 2, 'TileSpacing', 'loose', 'Padding', 'compact');
mimoColumns = {'cond_median_db', 'erank_median', 'capacity_10db'};
mimoLabels = {'Condition number (dB)', 'Effective rank (/9)', ...
    'MIMO capacity @ 10 dB (bit/s/Hz)'};

for metricIndex = 1:3
    for trajectoryIndex = 1:numel(trajectories)
        ax = nexttile(t5, (metricIndex - 1) * 2 + trajectoryIndex);
        hold(ax, 'on');
        for systemIndex = 1:numel(systems)
            rows = textMask(trajectoryMimo, 'trajectory', trajectories(trajectoryIndex)) & ...
                textMask(trajectoryMimo, 'system', systems(systemIndex));
            block = sortrows(trajectoryMimo(rows, :), 'distance_along_m');
            plot(ax, block.distance_along_m, tableColumn(block, mimoColumns{metricIndex}), ...
                'Color', colors(systemIndex, :), ...
                'LineStyle', lineStyles{systemIndex}, ...
                'Marker', markers{systemIndex}, 'MarkerSize', 4, ...
                'LineWidth', 2, 'DisplayName', systemLabels{systemIndex});
        end
        hold(ax, 'off');
        ylabel(ax, mimoLabels{metricIndex});
        title(ax, trajectories(trajectoryIndex));
        legend(ax, 'Location', 'best');
        if metricIndex == 3
            xlabel(ax, 'Distance along trajectory (m)');
        end
    end
end
title(t5, {'Synthetic 9x9 MIMO along the trajectory', ...
    'Each waypoint combines nine RX scenarios into a 9x9 matrix'}, ...
    'FontSize', 14, 'FontWeight', 'bold');
saveDisplayedFigure(f5, outputDir, '05_trajectory_mimo_metrics_matlab');

%% Figure 6 - pooled dan median-based spatial decorrelation
f6 = newVisibleFigure('06 - Spatial decorrelation', ...
    [125, 50, 1500, 880], surfaceColor);
t6 = tiledlayout(f6, 2, 2, 'TileSpacing', 'loose', 'Padding', 'compact');
spatialTables = {spatialPooled, spatialMedian};
spatialColumns = {'mean_spatial_decorrelation', 'median_pair_decorrelation'};
spatialNames = {'Pooled', 'Median-based'};

for trajectoryIndex = 1:numel(trajectories)
    for metricIndex = 1:2
        ax = nexttile(t6, (trajectoryIndex - 1) * 2 + metricIndex);
        sourceTable = spatialTables{metricIndex};
        hold(ax, 'on');
        for systemIndex = 1:numel(systems)
            rows = textMask(sourceTable, 'trajectory', trajectories(trajectoryIndex)) & ...
                textMask(sourceTable, 'system', systems(systemIndex));
            block = sortrows(sourceTable(rows, :), 'distance_along_m');
            plot(ax, block.distance_along_m, ...
                tableColumn(block, spatialColumns{metricIndex}), ...
                'Color', colors(systemIndex, :), ...
                'LineStyle', lineStyles{systemIndex}, ...
                'Marker', markers{systemIndex}, 'MarkerSize', 4, ...
                'LineWidth', 2, 'DisplayName', systemLabels{systemIndex});
        end
        hold(ax, 'off');
        ylim(ax, [0, 1.02]);
        xlabel(ax, 'Distance along trajectory (m)');
        ylabel(ax, 'Spatial decorrelation');
        title(ax, sprintf('%s: %s', trajectories(trajectoryIndex), ...
            spatialNames{metricIndex}));
        legend(ax, 'Location', 'best');
    end
end
title(t6, {'Spatial decorrelation: center TX element (index 4) x 9 RX', ...
    'Higher values indicate less-correlated responses across RX branches'}, ...
    'FontSize', 14, 'FontWeight', 'bold');
saveDisplayedFigure(f6, outputDir, '06_spatial_decorrelation_comparison_matlab');

%% Figure 7 - raw spatial difference power
f7 = newVisibleFigure('07 - Raw spatial difference power', ...
    [145, 100, 1450, 580], surfaceColor);
t7 = tiledlayout(f7, 1, 2, 'TileSpacing', 'loose', 'Padding', 'compact');
for trajectoryIndex = 1:numel(trajectories)
    ax = nexttile(t7);
    hold(ax, 'on');
    for systemIndex = 1:numel(systems)
        rows = textMask(spatialRaw, 'trajectory', trajectories(trajectoryIndex)) & ...
            textMask(spatialRaw, 'system', systems(systemIndex));
        block = sortrows(spatialRaw(rows, :), 'distance_along_m');
        rawDb = 10 * log10(max(block.mean_raw_difference_power, realmin));
        plot(ax, block.distance_along_m, rawDb, ...
            'Color', colors(systemIndex, :), ...
            'LineStyle', lineStyles{systemIndex}, ...
            'Marker', markers{systemIndex}, 'MarkerSize', 4, ...
            'LineWidth', 2, 'DisplayName', systemLabels{systemIndex});
    end
    hold(ax, 'off');
    xlabel(ax, 'Distance along trajectory (m)');
    ylabel(ax, '10 log10 mean raw difference power');
    title(ax, trajectories(trajectoryIndex));
    legend(ax, 'Location', 'best');
end
title(t7, {'Unnormalized spatial channel-power difference', ...
    'This metric retains path loss and RX-pattern gain'}, ...
    'FontSize', 14, 'FontWeight', 'bold');
saveDisplayedFigure(f7, outputDir, '07_raw_spatial_difference_power_matlab');

%% Figure 8 - ringkasan agregat
f8 = newVisibleFigure('08 - Aggregate summary', ...
    [165, 30, 1550, 940], surfaceColor);
t8 = tiledlayout(f8, 2, 3, 'TileSpacing', 'loose', 'Padding', 'compact');
aggregateMetrics = {'channel_magnitude_median_db', ...
    'capacity_median_bits_s_hz', ...
    'trajectory_mimo_capacity_median_10db', ...
    'trajectory_mimo_erank_median', ...
    'pooled_decorrelation', 'median_decorrelation'};
aggregateTitles = {'Median channel magnitude', 'Median link capacity', ...
    'Median MIMO capacity @ 10 dB', 'Median effective rank (/9)', ...
    'Pooled decorrelation', 'Median-based decorrelation'};
aggregateLabels = {'dB', 'bit/s/Hz', 'bit/s/Hz', ...
    'Effective rank', 'Decorrelation', 'Decorrelation'};

for panel = 1:6
    ax = nexttile(t8);
    values = nan(2, 2);
    for trajectoryIndex = 1:numel(trajectories)
        for systemIndex = 1:numel(systems)
            rows = textMask(summary, 'trajectory', trajectories(trajectoryIndex)) & ...
                textMask(summary, 'system', systems(systemIndex));
            values(trajectoryIndex, systemIndex) = ...
                tableColumn(summary(rows, :), aggregateMetrics{panel});
        end
    end
    groupedBars(ax, values, cellstr(trajectories), systemLabels, colors, '%.2f');
    if panel == 1
        legend(ax, systemLabels, 'Location', 'northwest', 'FontSize', 8);
    else
        legend(ax, 'off');
    end
    ylabel(ax, aggregateLabels{panel});
    title(ax, aggregateTitles{panel});
    if panel == 4
        ylim(ax, [0, 9]);
    elseif panel >= 5
        ylim(ax, [0, 1.05]);
    end
end
title(t8, {'Aggregate comparison: Lens vs Without Lens - 9 ISO TX', ...
    'Headline values are taken from notebook outputs through Section 14'}, ...
    'FontSize', 14, 'FontWeight', 'bold');
saveDisplayedFigure(f8, outputDir, '08_aggregate_comparison_matlab');

drawnow;
fprintf('\nSelesai: 8 figure ditampilkan dan disimpan.\n');
fprintf('Output MATLAB: %s\n', outputDir);
fprintf('Window figure sengaja tidak ditutup agar dapat diperiksa/interaksikan.\n');

%% Local helper functions
function tableData = readAnalysisCsv(path)
    if ~isfile(path)
        error('CSV tidak ditemukan: %s', path);
    end
    options = detectImportOptions(path, 'VariableNamingRule', 'preserve');
    tableData = readtable(path, options);
end

function values = tableColumn(tableData, columnName)
    if ~ismember(columnName, tableData.Properties.VariableNames)
        error('Kolom "%s" tidak ditemukan.', columnName);
    end
    values = tableData{:, columnName};
end

function mask = textMask(tableData, columnName, expectedValue)
    mask = string(tableData{:, columnName}) == string(expectedValue);
end

function validateInputs(summary, waypoint, trajectoryMimo, spatialPooled, ...
        spatialMedian, trajectories, systems)
    if height(summary) ~= 4
        error('comparison_summary.csv harus berisi empat kombinasi skenario.');
    end
    expectedWaypoints = [21, 37];
    for trajectoryIndex = 1:numel(trajectories)
        for systemIndex = 1:numel(systems)
            trajectoryName = trajectories(trajectoryIndex);
            systemName = systems(systemIndex);
            summaryRows = textMask(summary, 'trajectory', trajectoryName) & ...
                textMask(summary, 'system', systemName);
            if nnz(summaryRows) ~= 1
                error('Skenario %s / %s tidak unik.', trajectoryName, systemName);
            end
            rows = textMask(waypoint, 'trajectory', trajectoryName) & ...
                textMask(waypoint, 'system', systemName);
            if nnz(rows) ~= expectedWaypoints(trajectoryIndex) * 9
                error('Jumlah waypoint-RX tidak valid untuk %s / %s.', ...
                    trajectoryName, systemName);
            end
            rows = textMask(trajectoryMimo, 'trajectory', trajectoryName) & ...
                textMask(trajectoryMimo, 'system', systemName);
            if nnz(rows) ~= expectedWaypoints(trajectoryIndex)
                error('Jumlah baris MIMO tidak valid untuk %s / %s.', ...
                    trajectoryName, systemName);
            end
            rowsPooled = textMask(spatialPooled, 'trajectory', trajectoryName) & ...
                textMask(spatialPooled, 'system', systemName);
            rowsMedian = textMask(spatialMedian, 'trajectory', trajectoryName) & ...
                textMask(spatialMedian, 'system', systemName);
            if nnz(rowsPooled) ~= expectedWaypoints(trajectoryIndex) || ...
                    nnz(rowsMedian) ~= expectedWaypoints(trajectoryIndex)
                error('Jumlah baris spatial tidak valid untuk %s / %s.', ...
                    trajectoryName, systemName);
            end
        end
    end
end

function fig = newVisibleFigure(figureName, position, surfaceColor)
    fig = figure('Name', figureName, 'NumberTitle', 'off', ...
        'Color', surfaceColor, 'Visible', 'on', 'Position', position);
end

function [x, meanValue, minValue, maxValue] = aggregateByDistance(tableData, valueColumn)
    distance = tableData.distance_along_m_exact;
    value = tableColumn(tableData, valueColumn);
    [x, ~, group] = unique(distance, 'sorted');
    meanValue = accumarray(group, value, [], @mean);
    minValue = accumarray(group, value, [], @min);
    maxValue = accumarray(group, value, [], @max);
end

function categoricalBars(ax, values, labels, colors, numberFormat)
    values = values(:);
    x = 1:numel(values);
    bars = bar(ax, x, values, 0.62, 'FaceColor', 'flat', ...
        'EdgeColor', [48, 52, 59] / 255, 'LineWidth', 0.8);
    bars.CData = colors;
    xticks(ax, x);
    xticklabels(ax, labels);
    addBarLabels(ax, x(:), values, numberFormat);
    padBarAxis(ax, values);
end

function groupedBars(ax, values, categoryLabels, seriesLabels, colors, numberFormat)
    bars = bar(ax, values, 'grouped', 'EdgeColor', [48, 52, 59] / 255, ...
        'LineWidth', 0.8);
    for seriesIndex = 1:numel(bars)
        bars(seriesIndex).FaceColor = colors(seriesIndex, :);
        x = bars(seriesIndex).XEndPoints;
        y = bars(seriesIndex).YEndPoints;
        % Label langsung hanya untuk chart ringkas. Pada 9 kategori x 2
        % sistem, label angka saling bertumpuk dan mengurangi keterbacaan.
        if numel(values) <= 8
            addBarLabels(ax, x(:), y(:), numberFormat);
        end
    end
    xticks(ax, 1:size(values, 1));
    xticklabels(ax, categoryLabels);
    legend(ax, seriesLabels, 'Location', 'best', 'FontSize', 8);
    padBarAxis(ax, values(:));
end

function addBarLabels(ax, x, values, numberFormat)
    holdState = ishold(ax);
    hold(ax, 'on');
    span = max(values) - min([0; values]);
    if span <= 0
        span = max(abs(values));
    end
    if span <= 0
        span = 1;
    end
    offset = 0.025 * span;
    for index = 1:numel(values)
        if values(index) >= 0
            verticalAlignment = 'bottom';
            labelY = values(index) + offset;
        else
            verticalAlignment = 'top';
            labelY = values(index) - offset;
        end
        text(ax, x(index), labelY, sprintf(numberFormat, values(index)), ...
            'HorizontalAlignment', 'center', ...
            'VerticalAlignment', verticalAlignment, 'FontSize', 8, ...
            'Color', [48, 52, 59] / 255);
    end
    if ~holdState
        hold(ax, 'off');
    end
end

function padBarAxis(ax, values)
    low = min([0; values(:)]);
    high = max([0; values(:)]);
    span = high - low;
    if span <= 0
        span = 1;
    end
    ylim(ax, [low - 0.10 * span, high + 0.16 * span]);
end

function saveDisplayedFigure(fig, outputDir, baseName)
    drawnow;
    pngPath = fullfile(outputDir, [baseName, '.png']);
    figPath = fullfile(outputDir, [baseName, '.fig']);
    exportgraphics(fig, pngPath, 'Resolution', 180);
    savefig(fig, figPath);
    fprintf('Displayed and saved: %s.{png,fig}\n', fullfile(outputDir, baseName));
end
