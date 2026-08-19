%% plot_analysis_figures_matlab.m
% Plot ulang hasil analisis Lens 3x3, 5x5, dan 9x9 dengan MATLAB.
%
% Perilaku default:
%   1. Membaca CSV pada folder data/ tanpa menjalankan ulang Sionna RT.
%   2. MENAMPILKAN delapan figure sebagai window MATLAB (Visible = on).
%   3. Menyimpan setiap figure sebagai PNG dan MATLAB .fig di figures_matlab/.
%
% Jalankan dari folder mana pun:
%   run('Analisis_v4_ISO_TX_Lens_Order_3x3_5x5_9x9_Linear/plot_analysis_figures_matlab.m')
%
% Script memerlukan MATLAB R2019b atau lebih baru (tiledlayout/exportgraphics).

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

% Figure tetap ditampilkan setelah disimpan.
set(groot, 'defaultFigureVisible', 'on');

orders = [3, 5, 9];
orderLabels = {'3x3', '5x5', '9x9'};
colors = [31, 90, 133; 216, 145, 38; 139, 71, 113] / 255;
lineStyles = {'-', '--', '-.'};
markers = {'o', 's', '^'};
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

%% Load CSV hasil analisis
summary = readAnalysisCsv(fullfile(dataDir, 'comparison_summary.csv'));
rxConfig = readAnalysisCsv(fullfile(dataDir, 'rx_configurations_combined.csv'));
staticRx = readAnalysisCsv(fullfile(dataDir, 'static_summary_combined.csv'));
waypoint = readAnalysisCsv(fullfile(dataDir, 'waypoint_samples_combined.csv'));
trajectoryMimo = readAnalysisCsv(fullfile(dataDir, 'trajectory_mimo_combined.csv'));
spatialPooled = readAnalysisCsv(fullfile(dataDir, 'spatial_pooled_combined.csv'));
spatialMedian = readAnalysisCsv(fullfile(dataDir, 'spatial_median_combined.csv'));
spatialRaw = readAnalysisCsv(fullfile(dataDir, 'spatial_raw_combined.csv'));

validateInputs(summary, waypoint, trajectoryMimo, spatialPooled, spatialMedian, orders);

%% Figure 1 — geometri trajectory, aperture TX, dan sudut RX
f1 = newVisibleFigure('01 - Order geometry', [40, 60, 1550, 520], surfaceColor);
t1 = tiledlayout(f1, 1, 3, 'TileSpacing', 'loose', 'Padding', 'compact');

ax = nexttile(t1);
w9 = waypoint(waypoint.order_n == 9, :);
[~, firstRows] = unique(w9.waypoint, 'stable');
w9 = sortrows(w9(firstRows, :), 'waypoint');
plot(ax, w9.tx_center_x_m, w9.tx_center_y_m, '-o', ...
    'Color', colors(1, :), 'LineWidth', 2, 'MarkerSize', 4, ...
    'DisplayName', 'TX center');
hold(ax, 'on');
scatter(ax, w9.tx_center_x_m(1), w9.tx_center_y_m(1), 90, '^', ...
    'filled', 'MarkerFaceColor', colors(2, :), 'DisplayName', 'Start');
scatter(ax, w9.tx_center_x_m(end), w9.tx_center_y_m(end), 90, 'x', ...
    'LineWidth', 2.5, 'MarkerEdgeColor', colors(3, :), 'DisplayName', 'End');
hold(ax, 'off');
axis(ax, 'equal');
xlim(ax, [-10, 10]);
ylim(ax, [-10, 10]);
xlabel(ax, 'X (m)');
ylabel(ax, 'Y (m)');
title(ax, 'Identical linear trajectory');
legend(ax, 'Location', 'best');

ax = nexttile(t1);
hold(ax, 'on');
for k = 1:numel(orders)
    n = orders(k);
    offsetMm = (((0:n-1) - (n-1)/2) * 0.45) * 1000;
    plot(ax, offsetMm, repmat(n, 1, n), 'LineStyle', 'none', ...
        'Marker', markers{k}, 'MarkerSize', 8, 'Color', colors(k, :), ...
        'MarkerFaceColor', colors(k, :), 'DisplayName', orderLabels{k});
end
hold(ax, 'off');
yticks(ax, orders);
xlabel(ax, 'Y offset from TX centroid (mm)');
ylabel(ax, 'Order N');
title(ax, 'ISO TX array footprint');
legend(ax, 'Location', 'best');

ax = nexttile(t1);
hold(ax, 'on');
for k = 1:numel(orders)
    n = orders(k);
    rows = rxConfig.order_n == n;
    angles = sort(rxConfig.rx_lens_angle_deg(rows));
    plot(ax, angles, repmat(n, size(angles)), 'LineStyle', 'none', ...
        'Marker', markers{k}, 'MarkerSize', 8, 'Color', colors(k, :), ...
        'MarkerFaceColor', colors(k, :), 'DisplayName', orderLabels{k});
end
hold(ax, 'off');
yticks(ax, orders);
xlabel(ax, 'RX Lens angle (degrees)');
ylabel(ax, 'Order N');
title(ax, 'Lens RX pattern angular coverage');
legend(ax, 'Location', 'best');

title(t1, {'Lens order N x N geometry with an identical linear trajectory', ...
    'Element count, TX aperture, and RX angular sampling increase with order'}, ...
    'FontSize', 14, 'FontWeight', 'bold');
saveDisplayedFigure(f1, outputDir, '01_geometry_order_comparison_matlab');

%% Figure 2 — snapshot statis per sudut RX
f2 = newVisibleFigure('02 - Snapshot RX', [60, 80, 1550, 510], surfaceColor);
t2 = tiledlayout(f2, 1, 3, 'TileSpacing', 'loose', 'Padding', 'compact');
staticColumns = {'combined_gain_db', 'mean_|rho|_offdiag', 'capacity_10dB_bits/s/Hz'};
staticYLabels = {'Combined gain (dB)', 'Mean |rho| off-diagonal', 'Capacity (bit/s/Hz)'};
staticTitles = {'Combined gain', 'TX-branch correlation', 'Normalized capacity @ 10 dB'};
for panel = 1:3
    ax = nexttile(t2);
    hold(ax, 'on');
    for k = 1:numel(orders)
        rows = staticRx.order_n == orders(k);
        angle = staticRx.rx_lens_angle_deg(rows);
        value = tableColumn(staticRx(rows, :), staticColumns{panel});
        [angle, index] = sort(angle);
        value = value(index);
        plot(ax, angle, value, 'Color', colors(k, :), ...
            'LineStyle', lineStyles{k}, 'Marker', markers{k}, ...
            'LineWidth', 2, 'MarkerSize', 6, 'DisplayName', orderLabels{k});
    end
    hold(ax, 'off');
    xlabel(ax, 'RX Lens angle (degrees)');
    ylabel(ax, staticYLabels{panel});
    title(ax, staticTitles{panel});
    legend(ax, 'Location', 'best');
end
title(t2, {'Section 9 static snapshot by RX Lens angle', ...
    'Only the 0-degree angle is available for all three orders'}, ...
    'FontSize', 14, 'FontWeight', 'bold');
saveDisplayedFigure(f2, outputDir, '02_static_rx_by_order_matlab');

%% Figure 3 — scaling MIMO snapshot statis
f3 = newVisibleFigure('03 - Static MIMO scaling', [80, 45, 1550, 880], surfaceColor);
t3 = tiledlayout(f3, 2, 3, 'TileSpacing', 'loose', 'Padding', 'compact');
staticMimoValues = {
    summary.static_mimo_condition_db, ...
    summary.static_mimo_effective_rank, ...
    summary.static_mimo_erank_fraction, ...
    summary.static_mimo_capacity_10db, ...
    summary.static_mimo_capacity_per_order, ...
    summary.static_rx_correlation_mean};
staticMimoTitles = {'Conditioning - lower is better', 'Effective rank', ...
    'Dimension utilization', 'MIMO capacity @ 10 dB', 'Capacity per order', 'RX correlation'};
staticMimoYLabels = {'Condition number (dB)', 'Effective rank', 'Effective rank / N', ...
    'bit/s/Hz', 'bit/s/Hz/element', 'Mean |rho| off-diagonal'};
for panel = 1:6
    ax = nexttile(t3);
    categoricalBars(ax, staticMimoValues{panel}, orderLabels, colors, '%.2f');
    title(ax, staticMimoTitles{panel});
    ylabel(ax, staticMimoYLabels{panel});
end
title(t3, {'Synthetic/combined MIMO at the Section 10 static snapshot', ...
    'Each N x N matrix is constructed from N sequential N x 1 simulations'}, ...
    'FontSize', 14, 'FontWeight', 'bold');
saveDisplayedFigure(f3, outputDir, '03_static_mimo_scaling_matlab');

%% Figure 4 — SNR dan kapasitas link sepanjang trajectory
f4 = newVisibleFigure('04 - Link along trajectory', [100, 100, 1500, 560], surfaceColor);
t4 = tiledlayout(f4, 1, 2, 'TileSpacing', 'loose', 'Padding', 'compact');
channelColumns = {'snr_db_log_rounded', 'capacity_bits_s_hz_log_rounded'};
channelTitles = {'SNR along the trajectory', 'Link capacity along the trajectory'};
channelYLabels = {'Mean SNR across RX branches (dB)', 'Mean capacity across RX branches (bit/s/Hz)'};
for panel = 1:2
    ax = nexttile(t4);
    hold(ax, 'on');
    lineHandles = gobjects(numel(orders), 1);
    for k = 1:numel(orders)
        rows = waypoint.order_n == orders(k);
        [x, meanValue, minValue, maxValue] = aggregateByDistance( ...
            waypoint(rows, :), channelColumns{panel});
        fill(ax, [x; flipud(x)], [minValue; flipud(maxValue)], colors(k, :), ...
            'FaceAlpha', 0.07, 'EdgeColor', 'none', 'HandleVisibility', 'off');
        lineHandles(k) = plot(ax, x, meanValue, 'Color', colors(k, :), ...
            'LineStyle', lineStyles{k}, 'Marker', markers{k}, ...
            'LineWidth', 2, 'MarkerSize', 5, 'DisplayName', orderLabels{k});
    end
    if panel == 2
        yline(ax, 1, '-', 'Outage threshold', 'Color', inkColor, ...
            'LineWidth', 1, 'HandleVisibility', 'off');
    end
    hold(ax, 'off');
    xlabel(ax, 'Distance along trajectory (m)');
    ylabel(ax, channelYLabels{panel});
    title(ax, channelTitles{panel});
    legend(ax, lineHandles, orderLabels, 'Location', 'best');
end
title(t4, {'Section 11 link performance', ...
    'Lines = RX mean; bands = minimum-to-maximum range across RX branches'}, ...
    'FontSize', 14, 'FontWeight', 'bold');
saveDisplayedFigure(f4, outputDir, '04_channel_along_trajectory_matlab');

%% Figure 5 — MIMO sepanjang trajectory
f5 = newVisibleFigure('05 - Trajectory MIMO', [120, 50, 1450, 880], surfaceColor);
t5 = tiledlayout(f5, 2, 2, 'TileSpacing', 'loose', 'Padding', 'compact');
mimoColumns = {'cond_median_db', 'erank_median', 'erank_fraction', 'capacity_10db'};
mimoTitles = {'Conditioning', 'Effective rank', 'Dimension utilization', 'MIMO capacity @ 10 dB'};
mimoYLabels = {'Condition number (dB)', 'Effective rank', 'Effective rank / N', 'bit/s/Hz'};
for panel = 1:4
    ax = nexttile(t5);
    hold(ax, 'on');
    for k = 1:numel(orders)
        n = orders(k);
        rows = trajectoryMimo.order_n == n;
        block = sortrows(trajectoryMimo(rows, :), 'distance_along_m');
        if strcmp(mimoColumns{panel}, 'erank_fraction')
            value = block.erank_median / n;
        else
            value = tableColumn(block, mimoColumns{panel});
        end
        plot(ax, block.distance_along_m, value, 'Color', colors(k, :), ...
            'LineStyle', lineStyles{k}, 'Marker', markers{k}, ...
            'LineWidth', 2, 'MarkerSize', 5, 'DisplayName', orderLabels{k});
    end
    hold(ax, 'off');
    xlabel(ax, 'Distance along trajectory (m)');
    ylabel(ax, mimoYLabels{panel});
    title(ax, mimoTitles{panel});
    legend(ax, 'Location', 'best');
end
title(t5, {'Synthetic MIMO along the trajectory - Section 11c', ...
    'Higher order increases absolute capacity but reduces per-dimension efficiency'}, ...
    'FontSize', 14, 'FontWeight', 'bold');
saveDisplayedFigure(f5, outputDir, '05_trajectory_mimo_scaling_matlab');

%% Figure 6 — pooled dan median-based spatial decorrelation
f6 = newVisibleFigure('06 - Spatial decorrelation', [140, 110, 1500, 560], surfaceColor);
t6 = tiledlayout(f6, 1, 2, 'TileSpacing', 'loose', 'Padding', 'compact');
spatialTables = {spatialPooled, spatialMedian};
spatialColumns = {'mean_spatial_decorrelation', 'median_pair_decorrelation'};
spatialTitles = {'Pooled decorrelation', 'Median-based decorrelation'};
centerIndices = [1, 2, 4];
for panel = 1:2
    ax = nexttile(t6);
    hold(ax, 'on');
    sourceTable = spatialTables{panel};
    for k = 1:numel(orders)
        rows = sourceTable.order_n == orders(k);
        block = sortrows(sourceTable(rows, :), 'distance_along_m');
        plot(ax, block.distance_along_m, tableColumn(block, spatialColumns{panel}), ...
            'Color', colors(k, :), 'LineStyle', lineStyles{k}, ...
            'Marker', markers{k}, 'LineWidth', 2, 'MarkerSize', 5, ...
            'DisplayName', sprintf('%s (TX %d)', orderLabels{k}, centerIndices(k)));
    end
    hold(ax, 'off');
    ylim(ax, [0, 1]);
    xlabel(ax, 'Distance along trajectory (m)');
    ylabel(ax, 'Spatial decorrelation');
    title(ax, spatialTitles{panel});
    legend(ax, 'Location', 'best');
end
title(t6, {'Spatial decorrelation - Sections 12 and 14', ...
    'All orders use the center TX element: indices 1, 2, and 4'}, ...
    'FontSize', 14, 'FontWeight', 'bold');
saveDisplayedFigure(f6, outputDir, '06_spatial_decorrelation_by_order_matlab');

%% Figure 7 — raw spatial difference power
f7 = newVisibleFigure('07 - Raw spatial difference', [160, 140, 1400, 560], surfaceColor);
ax = axes(f7);
hold(ax, 'on');
for k = 1:numel(orders)
    rows = spatialRaw.order_n == orders(k);
    block = sortrows(spatialRaw(rows, :), 'distance_along_m');
    rawDb = 10 * log10(max(block.mean_raw_difference_power, realmin));
    plot(ax, block.distance_along_m, rawDb, 'Color', colors(k, :), ...
        'LineStyle', lineStyles{k}, 'Marker', markers{k}, ...
        'LineWidth', 2, 'MarkerSize', 5, ...
        'DisplayName', sprintf('%s (TX %d)', orderLabels{k}, centerIndices(k)));
end
hold(ax, 'off');
xlabel(ax, 'Distance along trajectory (m)');
ylabel(ax, '10 log10 mean raw difference power');
title(ax, {'Unnormalized spatial channel-power difference', ...
    'Section 13 retains path loss and RX-pattern gain'});
legend(ax, 'Location', 'best');
saveDisplayedFigure(f7, outputDir, '07_raw_spatial_difference_by_order_matlab');

%% Figure 8 — ringkasan agregat
f8 = newVisibleFigure('08 - Aggregate summary', [180, 45, 1550, 880], surfaceColor);
t8 = tiledlayout(f8, 2, 3, 'TileSpacing', 'loose', 'Padding', 'compact');
aggregateValues = {
    summary.capacity_median_bits_s_hz, ...
    summary.trajectory_mimo_capacity_median_10db, ...
    summary.trajectory_mimo_capacity_per_order, ...
    summary.trajectory_mimo_erank_fraction, ...
    summary.pooled_decorrelation, ...
    summary.median_decorrelation};
aggregateTitles = {'Median link capacity', 'Median MIMO capacity @ 10 dB', ...
    'MIMO capacity per order', 'MIMO dimension utilization', ...
    'Pooled decorrelation', 'Median-based decorrelation'};
aggregateYLabels = {'bit/s/Hz', 'bit/s/Hz', 'bit/s/Hz/element', ...
    'Effective rank / N', 'Decorrelation', 'Decorrelation'};
for panel = 1:6
    ax = nexttile(t8);
    categoricalBars(ax, aggregateValues{panel}, orderLabels, colors, '%.2f');
    title(ax, aggregateTitles{panel});
    ylabel(ax, aggregateYLabels{panel});
    if panel >= 4
        ylim(ax, [0, 1.05]);
    end
end
title(t8, {'Order comparison: 3x3, 5x5, and 9x9 - ISO TX, Lens RX', ...
    'Headline values are taken from notebook outputs through Section 14'}, ...
    'FontSize', 14, 'FontWeight', 'bold');
saveDisplayedFigure(f8, outputDir, '08_aggregate_order_comparison_matlab');

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

function validateInputs(summary, waypoint, trajectoryMimo, spatialPooled, spatialMedian, orders)
    actualOrders = sort(summary.order_n(:))';
    if ~isequal(actualOrders, orders)
        error('Order pada comparison_summary.csv harus [3 5 9].');
    end
    for n = orders
        if height(waypoint(waypoint.order_n == n, :)) ~= 21 * n
            error('Jumlah baris waypoint untuk order %d tidak sama dengan 21 x N.', n);
        end
        if height(trajectoryMimo(trajectoryMimo.order_n == n, :)) ~= 21
            error('Jumlah baris trajectory MIMO untuk order %d bukan 21.', n);
        end
        if height(spatialPooled(spatialPooled.order_n == n, :)) ~= 21 || ...
                height(spatialMedian(spatialMedian.order_n == n, :)) ~= 21
            error('Jumlah baris spatial untuk order %d bukan 21.', n);
        end
    end
    expectedCenters = floor(orders / 2);
    if any(summary.selected_tx_index(:)' ~= expectedCenters)
        error('Selected TX spatial harus elemen tengah: indeks [1 2 4].');
    end
end

function fig = newVisibleFigure(figureName, position, surfaceColor)
    fig = figure('Name', figureName, 'NumberTitle', 'off', ...
        'Color', surfaceColor, 'Visible', 'on', 'Position', position);
end

function [x, meanValue, minValue, maxValue] = aggregateByDistance(tableData, valueColumn)
    distance = tableData.distance_along_m;
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
    yRange = max(values) - min([0; values]);
    if yRange <= 0
        yRange = 1;
    end
    yOffset = 0.025 * yRange;
    for i = 1:numel(values)
        text(ax, x(i), values(i) + yOffset, sprintf(numberFormat, values(i)), ...
            'HorizontalAlignment', 'center', 'VerticalAlignment', 'bottom', ...
            'FontSize', 9, 'Color', [48, 52, 59] / 255);
    end
    upper = max(values) + 5 * yOffset;
    if all(values >= 0)
        ylim(ax, [0, max(upper, eps)]);
    end
end

function saveDisplayedFigure(fig, outputDir, baseName)
    drawnow;
    pngPath = fullfile(outputDir, [baseName, '.png']);
    figPath = fullfile(outputDir, [baseName, '.fig']);
    exportgraphics(fig, pngPath, 'Resolution', 180);
    savefig(fig, figPath);
    fprintf('Displayed and saved: %s.{png,fig}\n', fullfile(outputDir, baseName));
end
