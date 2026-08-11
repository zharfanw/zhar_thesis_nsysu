%% make_figures.m
% MATLAB port of make_figures.py -- builds the same 5 lens-vs-no-lens
% comparison figures from the parsed CSV data under asset/data/, and
% DISPLAYS them as normal (visible) figure windows, in addition to
% saving PNG copies into asset/figures/ (with a "_matlab" suffix so the
% Python-generated originals referenced by the report are not overwritten).
%
% Run from anywhere -- paths are resolved relative to this file's location
% (asset/scripts/), so the repo can be checked out anywhere.

clear; clc;

here    = fileparts(mfilename('fullpath'));   % .../asset/scripts
assetDir = fileparts(here);                    % .../asset
dataDir  = fullfile(assetDir, 'data');
figDir   = fullfile(assetDir, 'figures');
if ~exist(figDir, 'dir')
    mkdir(figDir);
end

%% ---- palette (dataviz skill reference palette, light mode) ----
cSurface   = [252 252 251] / 255;
cPrimary   = [11 11 11] / 255;
cSecondary = [82 81 78] / 255;
cMuted     = [137 135 129] / 255;
cGrid      = [225 224 217] / 255;
cBaseline  = [195 194 183] / 255;
cBlue      = [42 120 214] / 255;   % categorical slot 1 -- "without lens"
cOrange    = [235 104 52] / 255;   % categorical slot 2 -- "with lens"
cRed       = [227 73 72] / 255;    % diverging pole (negative)

angles = [60 45 30 15 0 -15 -30 -45 -60];

%% ---- load data ----
wolens       = readtable(fullfile(dataDir, 'wolens_per_drop_rx.csv'));
lens         = readtable(fullfile(dataDir, 'lens_per_drop_rx.csv'));
perRxWolens  = readtable(fullfile(dataDir, 'wolens_per_rx_summary.csv'));
perRxLens    = readtable(fullfile(dataDir, 'lens_per_rx_summary.csv'));
mimoWolens   = readtable(fullfile(dataDir, 'wolens_mimo_per_drop.csv'));
mimoLens     = readtable(fullfile(dataDir, 'lens_mimo_per_drop.csv'));
paired       = readtable(fullfile(dataDir, 'paired_diff_per_drop_rx.csv'));

%% ============================================================
%  Figure 0a / 0b -- standalone (single-scenario) results, one per
%  notebook, BEFORE the two scenarios are combined for comparison.
%% ============================================================
plotIndividualScenario(wolens, perRxWolens, mimoWolens, cBlue, 'Without lens', ...
    '0a', figDir, cSurface, cPrimary, cSecondary, cMuted, cGrid, cBaseline, angles);
plotIndividualScenario(lens, perRxLens, mimoLens, cOrange, 'With lens', ...
    '0b', figDir, cSurface, cPrimary, cSecondary, cMuted, cGrid, cBaseline, angles);

%% ============================================================
%  Figure 1 -- aggregate capacity: box + empirical CDF
%% ============================================================
f1 = figure('Name', 'Fig 1 - Aggregate capacity', 'Color', cSurface, ...
    'Position', [80 80 1100 500]);
t1 = tiledlayout(f1, 1, 2, 'TileSpacing', 'loose', 'Padding', 'compact');

% Numeric grouping (1 = without lens, 2 = with lens) keeps box order
% deterministic left-to-right -- boxplot would otherwise sort cell-string
% group labels alphabetically, which silently swaps the two boxes.
colorOrder = {cBlue, cOrange};
grpNum = [ones(height(wolens), 1); 2 * ones(height(lens), 1)];
grpLabels = {'Without lens (n=180)', 'With lens (n=180)'};

nexttile(t1);
boxData = [wolens.capacity_bits_s_hz; lens.capacity_bits_s_hz];
bx = boxplot(boxData, grpNum, 'Labels', grpLabels, 'Colors', 'k', 'Symbol', 'o');
set(bx, 'LineWidth', 1.1);
colorBoxplot(bx, colorOrder);
ylabel('Capacity (bit/s/Hz)');
title('Aggregate capacity distribution', 'FontWeight', 'bold');
grid on; box off;
set(gca, 'Color', cSurface, 'GridColor', cGrid, 'XColor', cMuted, 'YColor', cMuted);

nexttile(t1);
hold on;
[xw, yw] = ecdfXY(wolens.capacity_bits_s_hz);
[xl, yl] = ecdfXY(lens.capacity_bits_s_hz);
plot(xw, yw, 'Color', cBlue, 'LineWidth', 2, 'DisplayName', 'Without lens');
plot(xl, yl, 'Color', cOrange, 'LineWidth', 2, 'DisplayName', 'With lens');
yline(0.5, '--', 'Color', cBaseline, 'LineWidth', 0.8, 'HandleVisibility', 'off');
yline(0.05, ':', 'Color', cBaseline, 'LineWidth', 0.8, 'HandleVisibility', 'off');
xlabel('Capacity (bit/s/Hz)');
ylabel('Empirical CDF');
title('Capacity CDF (all drops x angles)', 'FontWeight', 'bold');
legend('Location', 'southeast', 'Box', 'off');
grid on; box off; hold off;
set(gca, 'Color', cSurface, 'GridColor', cGrid, 'XColor', cMuted, 'YColor', cMuted);

title(t1, 'Fig. 1 -- Aggregate SISO capacity: without lens vs with lens', ...
    'FontWeight', 'bold', 'FontSize', 13);
drawnow;
exportgraphics(f1, fullfile(figDir, 'fig1_capacity_aggregate_matlab.png'), 'Resolution', 200);

%% ============================================================
%  Figure 2 -- median capacity vs RX angle, with 5-95% band
%% ============================================================
f2 = figure('Name', 'Fig 2 - Capacity vs angle', 'Color', cSurface, ...
    'Position', [120 100 850 520]);
hold on;

plotBandLine(perRxLens, cOrange);
plotBandLine(perRxWolens, cBlue);

pw = plot(perRxWolens.rx_lens_angle_deg, perRxWolens.capacity_median, '-o', ...
    'Color', cBlue, 'MarkerFaceColor', cBlue, 'LineWidth', 2.2, 'MarkerSize', 6, ...
    'DisplayName', 'Without lens');
pl = plot(perRxLens.rx_lens_angle_deg, perRxLens.capacity_median, '-o', ...
    'Color', cOrange, 'MarkerFaceColor', cOrange, 'LineWidth', 2.2, 'MarkerSize', 6, ...
    'DisplayName', 'With lens');

[bestVal, bestIdx] = max(perRxLens.capacity_median);
[worstVal, worstIdx] = min(perRxLens.capacity_median);
text(perRxLens.rx_lens_angle_deg(bestIdx) - 30, bestVal + 1.0, ...
    sprintf('best: %+d deg\n%.2f bit/s/Hz', perRxLens.rx_lens_angle_deg(bestIdx), bestVal), ...
    'FontSize', 8.5, 'Color', cSecondary);
text(perRxLens.rx_lens_angle_deg(worstIdx) + 4, worstVal - 1.6, ...
    sprintf('weakest: %+d deg\n%.2f bit/s/Hz', perRxLens.rx_lens_angle_deg(worstIdx), worstVal), ...
    'FontSize', 8.5, 'Color', cSecondary);

set(gca, 'XDir', 'reverse', 'XTick', sort(angles));
xlabel('RX lens angle (deg)');
ylabel('Capacity (bit/s/Hz)');
title('Fig. 2 -- Median capacity per RX angle (shaded band = 5th-95th percentile)', ...
    'FontWeight', 'bold');
legend([pw pl], 'Location', 'north', 'Orientation', 'horizontal', 'Box', 'off');
grid on; box off; hold off;
set(gca, 'Color', cSurface, 'GridColor', cGrid, 'XColor', cMuted, 'YColor', cMuted);
drawnow;
exportgraphics(f2, fullfile(figDir, 'fig2_capacity_vs_angle_matlab.png'), 'Resolution', 200);

%% ============================================================
%  Figure 3 -- paired per-drop capacity difference, by angle
%% ============================================================
f3 = figure('Name', 'Fig 3 - Paired diff by angle', 'Color', cSurface, ...
    'Position', [150 120 1180 500]);
t3 = tiledlayout(f3, 1, 2, 'TileSpacing', 'loose', 'Padding', 'compact');

medDiff = zeros(size(angles));
winRate = zeros(size(angles));
for i = 1:length(angles)
    mask = paired.rx_lens_angle_deg == angles(i);
    medDiff(i) = median(paired.capacity_diff(mask));
    winRate(i) = 100 * mean(paired.capacity_diff(mask) > 0);
end

nexttile(t3);
barColors = repmat(cBlue, length(angles), 1);
barColors(medDiff < 0, :) = repmat(cRed, sum(medDiff < 0), 1);
bh = bar(categorical(string(angles), string(angles)), medDiff, 0.62, 'FaceColor', 'flat');
bh.CData = barColors;
yline(0, 'Color', cBaseline, 'LineWidth', 1.0, 'HandleVisibility', 'off');
for i = 1:length(angles)
    va = 'bottom'; dy = 0.03;
    if medDiff(i) < 0, va = 'top'; dy = -0.03; end
    text(i, medDiff(i) + dy, sprintf('%+.2f', medDiff(i)), ...
        'HorizontalAlignment', 'center', 'VerticalAlignment', va, ...
        'FontSize', 8, 'Color', cSecondary);
end
xlabel('RX lens angle (deg)');
ylabel('Median paired capacity diff (bit/s/Hz)');
title('Median (lens - no lens) per angle, paired by identical TX geometry', ...
    'FontWeight', 'bold', 'FontSize', 10);
grid on; box off;
set(gca, 'Color', cSurface, 'GridColor', cGrid, 'XColor', cMuted, 'YColor', cMuted);

nexttile(t3);
bh2 = bar(categorical(string(angles), string(angles)), winRate, 0.62, ...
    'FaceColor', cOrange, 'FaceAlpha', 0.85);
yline(50, '--', 'Color', cBaseline, 'LineWidth', 1.0, 'HandleVisibility', 'off');
ylim([0 100]);
for i = 1:length(angles)
    text(i, winRate(i) + 3, sprintf('%.0f%%', winRate(i)), ...
        'HorizontalAlignment', 'center', 'FontSize', 8, 'Color', cSecondary);
end
xlabel('RX lens angle (deg)');
ylabel('Drops where lens wins (%)');
title('Lens win-rate per angle (of 20 paired drops)', 'FontWeight', 'bold', 'FontSize', 10);
grid on; box off;
set(gca, 'Color', cSurface, 'GridColor', cGrid, 'XColor', cMuted, 'YColor', cMuted);

title(t3, 'Fig. 3 -- Paired per-drop capacity difference (180 identical-TX pairs)', ...
    'FontWeight', 'bold', 'FontSize', 13);
drawnow;
exportgraphics(f3, fullfile(figDir, 'fig3_paired_diff_by_angle_matlab.png'), 'Resolution', 200);

%% ============================================================
%  Figure 4 -- RMS delay spread comparison
%% ============================================================
f4 = figure('Name', 'Fig 4 - Delay spread', 'Color', cSurface, ...
    'Position', [180 140 1100 500]);
t4 = tiledlayout(f4, 1, 2, 'TileSpacing', 'loose', 'Padding', 'compact');

nexttile(t4);
boxData = [wolens.rms_delay_spread_ns; lens.rms_delay_spread_ns];
bx = boxplot(boxData, grpNum, 'Labels', {'Without lens', 'With lens'}, 'Colors', 'k', 'Symbol', 'o');
set(bx, 'LineWidth', 1.1);
colorBoxplot(bx, colorOrder);
ylabel('RMS delay spread (ns)');
title('Aggregate delay-spread distribution', 'FontWeight', 'bold');
grid on; box off;
set(gca, 'Color', cSurface, 'GridColor', cGrid, 'XColor', cMuted, 'YColor', cMuted);

nexttile(t4);
hold on;
dsW = grpstatsMedian(wolens, angles);
dsL = grpstatsMedian(lens, angles);
plot(angles, dsW, '-o', 'Color', cBlue, 'MarkerFaceColor', cBlue, ...
    'LineWidth', 2.2, 'MarkerSize', 6, 'DisplayName', 'Without lens');
plot(angles, dsL, '-o', 'Color', cOrange, 'MarkerFaceColor', cOrange, ...
    'LineWidth', 2.2, 'MarkerSize', 6, 'DisplayName', 'With lens');
set(gca, 'XDir', 'reverse', 'XTick', sort(angles));
xlabel('RX lens angle (deg)');
ylabel('Median RMS delay spread (ns)');
title('Median delay spread per angle', 'FontWeight', 'bold');
legend('Box', 'off');
grid on; box off; hold off;
set(gca, 'Color', cSurface, 'GridColor', cGrid, 'XColor', cMuted, 'YColor', cMuted);

title(t4, 'Fig. 4 -- RMS delay spread: without lens vs with lens', ...
    'FontWeight', 'bold', 'FontSize', 13);
drawnow;
exportgraphics(f4, fullfile(figDir, 'fig4_delay_spread_matlab.png'), 'Resolution', 200);

%% ============================================================
%  Figure 5 -- virtual 9x9 MIMO conditioning, per drop (20 drops)
%% ============================================================
f5 = figure('Name', 'Fig 5 - MIMO conditioning', 'Color', cSurface, ...
    'Position', [200 160 1300 480]);
t5 = tiledlayout(f5, 1, 3, 'TileSpacing', 'loose', 'Padding', 'compact');

mimoGrpNum = [ones(height(mimoWolens), 1); 2 * ones(height(mimoLens), 1)];
mimoLabels = {'Without lens', 'With lens'};

nexttile(t5);
drawPairedBox([mimoWolens.cond_median_db; mimoLens.cond_median_db], mimoGrpNum, mimoLabels, colorOrder);
ylabel('Condition number (dB)');
title('Condition number', 'FontWeight', 'bold', 'FontSize', 10);
set(gca, 'Color', cSurface, 'GridColor', cGrid, 'XColor', cMuted, 'YColor', cMuted);

nexttile(t5);
drawPairedBox([mimoWolens.erank_median; mimoLens.erank_median], mimoGrpNum, mimoLabels, colorOrder);
yline(9, ':', '9 = full rank', 'Color', cMuted, 'LineWidth', 0.8, 'FontSize', 8, ...
    'LabelHorizontalAlignment', 'left');
ylabel('Effective rank (of 9)');
title('Effective rank', 'FontWeight', 'bold', 'FontSize', 10);
set(gca, 'Color', cSurface, 'GridColor', cGrid, 'XColor', cMuted, 'YColor', cMuted);

nexttile(t5);
drawPairedBox([mimoWolens.capacity_10db; mimoLens.capacity_10db], mimoGrpNum, mimoLabels, colorOrder);
ylabel('Capacity @ 10 dB SNR (bit/s/Hz)');
title('Virtual 9x9 MIMO capacity', 'FontWeight', 'bold', 'FontSize', 10);
set(gca, 'Color', cSurface, 'GridColor', cGrid, 'XColor', cMuted, 'YColor', cMuted);

title(t5, 'Fig. 5 -- Virtual 9x9 MIMO conditioning across 20 drops (not a physical single-RX result)', ...
    'FontWeight', 'bold', 'FontSize', 12.5);
drawnow;
exportgraphics(f5, fullfile(figDir, 'fig5_mimo_conditioning_matlab.png'), 'Resolution', 200);

fprintf('Done. 5 figures displayed and saved to %s (*_matlab.png)\n', figDir);

%% ================= helper functions =================
function [x, y] = ecdfXY(v)
    v = sort(v);
    n = numel(v);
    x = v;
    y = (1:n)' / n;
end

function plotBandLine(perRx, color)
    d = sortrows(perRx, 'rx_lens_angle_deg', 'descend');
    xx = [d.rx_lens_angle_deg; flipud(d.rx_lens_angle_deg)];
    yy = [d.capacity_p05; flipud(d.capacity_p95)];
    patch(xx, yy, color, 'FaceAlpha', 0.15, 'EdgeColor', 'none', 'HandleVisibility', 'off');
end

function med = grpstatsMedian(tbl, angles)
    med = zeros(size(angles));
    for i = 1:length(angles)
        med(i) = median(tbl.rms_delay_spread_ns(tbl.rx_lens_angle_deg == angles(i)));
    end
end

function drawPairedBox(data, grpNum, labels, colorOrder)
    % grpNum must be numeric (1, 2, ...) so box order is deterministic --
    % boxplot sorts cell-string group labels alphabetically, which can
    % silently swap which box gets which color.
    bx = boxplot(data, grpNum, 'Labels', labels, 'Colors', 'k', 'Symbol', 'o');
    set(bx, 'LineWidth', 1.1);
    colorBoxplot(bx, colorOrder);
    grid on; box off;
end

function colorBoxplot(bx, colorOrder)
    % bx is the handle matrix returned by boxplot(); row 5 = box outline
    % (per MATLAB's documented row order: whiskers, adjacent values, box,
    % median, outliers), one column per group in the same left-to-right
    % order as the numeric group values / 'Labels'.
    boxRow = bx(5, :);
    for g = 1:numel(boxRow)
        p = patch(get(boxRow(g), 'XData'), get(boxRow(g), 'YData'), colorOrder{g}, ...
            'FaceAlpha', 0.85, 'EdgeColor', colorOrder{g});
        uistack(p, 'bottom'); % keep the median/whisker lines visible on top of the fill
    end
end

function plotIndividualScenario(df, perRx, mimoDf, color, label, tag, figDir, ...
        cSurface, cPrimary, cSecondary, cMuted, cGrid, cBaseline, angles)
    % Standalone (single-scenario) figure: capacity distribution, capacity
    % per angle, delay spread per angle, and the 3 virtual-MIMO metrics --
    % all for ONE scenario only, before it is combined with the other one
    % for comparison in fig1-fig5.
    fig = figure('Name', ['Fig ' tag ' - Standalone ' label], 'Color', cSurface, ...
        'Position', [100 100 1350 860]);
    t = tiledlayout(fig, 2, 3, 'TileSpacing', 'loose', 'Padding', 'compact');

    % (a) capacity distribution -- histogram + median/p05/p95 markers
    nexttile(t);
    vals = df.capacity_bits_s_hz;
    % percentileType7 (not MATLAB's prctile/quantile) matches numpy's default
    % 'linear' interpolation, which is what the Python script uses for these
    % same p05/p95 markers -- keeps the two toolchains numerically identical.
    medC = median(vals); p05C = percentileType7(vals, 5); p95C = percentileType7(vals, 95);
    histogram(vals, 20, 'FaceColor', color, 'FaceAlpha', 0.85, 'EdgeColor', cSurface);
    hold on;
    xline(medC, '-', sprintf('median %.2f', medC), 'Color', cPrimary, 'LineWidth', 1.6);
    xline(p05C, ':', sprintf('p05 %.2f', p05C), 'Color', cMuted, 'LineWidth', 1.0);
    xline(p95C, ':', sprintf('p95 %.2f', p95C), 'Color', cMuted, 'LineWidth', 1.0);
    xlabel('Capacity (bit/s/Hz)');
    ylabel('Count (of 180 drop x angle)');
    title('Capacity distribution', 'FontWeight', 'bold', 'FontSize', 10.5);
    grid on; box off; hold off;
    set(gca, 'Color', cSurface, 'GridColor', cGrid, 'XColor', cMuted, 'YColor', cMuted);

    % (b) capacity vs angle, median +- 5-95%
    nexttile(t);
    hold on;
    plotBandLine(perRx, color);
    d = sortrows(perRx, 'rx_lens_angle_deg', 'descend');
    plot(d.rx_lens_angle_deg, d.capacity_median, '-o', 'Color', color, ...
        'MarkerFaceColor', color, 'LineWidth', 2.2, 'MarkerSize', 6);
    set(gca, 'XDir', 'reverse', 'XTick', sort(angles));
    xlabel('RX lens angle (deg)');
    ylabel('Capacity (bit/s/Hz)');
    title('Capacity per RX angle', 'FontWeight', 'bold', 'FontSize', 10.5);
    grid on; box off; hold off;
    set(gca, 'Color', cSurface, 'GridColor', cGrid, 'XColor', cMuted, 'YColor', cMuted);

    % (c) RMS delay spread vs angle (median)
    nexttile(t);
    dsVals = grpstatsMedian(df, angles);
    plot(angles, dsVals, '-o', 'Color', color, 'MarkerFaceColor', color, ...
        'LineWidth', 2.2, 'MarkerSize', 6);
    set(gca, 'XDir', 'reverse', 'XTick', sort(angles));
    xlabel('RX lens angle (deg)');
    ylabel('Median RMS delay spread (ns)');
    title('Delay spread per RX angle', 'FontWeight', 'bold', 'FontSize', 10.5);
    grid on; box off;
    set(gca, 'Color', cSurface, 'GridColor', cGrid, 'XColor', cMuted, 'YColor', cMuted);

    % (d)-(f) virtual 9x9 MIMO conditioning across the 20 drops (this scenario only)
    mimoCols   = {'cond_median_db', 'erank_median', 'capacity_10db'};
    mimoYLabel = {'Condition number (dB)', 'Effective rank (of 9)', 'Capacity @ 10 dB SNR (bit/s/Hz)'};
    mimoTitle  = {'Condition number', 'Effective rank', 'Virtual 9x9 MIMO capacity'};
    for k = 1:3
        nexttile(t);
        bx = boxplot(mimoDf.(mimoCols{k}), ones(height(mimoDf), 1), ...
            'Labels', {label}, 'Colors', 'k', 'Symbol', 'o');
        set(bx, 'LineWidth', 1.1);
        colorBoxplot(bx, {color});
        if k == 2
            yline(9, ':', '9 = full rank', 'Color', cMuted, 'LineWidth', 0.8, 'FontSize', 8);
        end
        ylabel(mimoYLabel{k});
        title(mimoTitle{k}, 'FontWeight', 'bold', 'FontSize', 10.5);
        grid on; box off;
        set(gca, 'Color', cSurface, 'GridColor', cGrid, 'XColor', cMuted, 'YColor', cMuted);
    end

    title(t, sprintf(['Fig. %s -- Standalone results, %s (20 drops x 9 angles = 180 rows; ' ...
        'not yet compared to the other scenario)'], tag, label), ...
        'FontWeight', 'bold', 'FontSize', 12.5);
    drawnow;
    fname = sprintf('fig%s_%s_individual_matlab.png', tag, lower(strrep(label, ' ', '_')));
    exportgraphics(fig, fullfile(figDir, fname), 'Resolution', 200);
end

function y = percentileType7(x, p)
    % Linear-interpolation percentile (R type 7 / Hazen's rival), matching
    % numpy.percentile's default 'linear' method exactly. MATLAB's own
    % prctile/quantile default to a different convention (type 5, using
    % (k-0.5)/n ranks), which gives visibly different p05/p95 values on a
    % small (n=180) sample -- this keeps the MATLAB and Python figures
    % numerically identical instead of just "close".
    x = sort(x(:));
    n = numel(x);
    h = (p / 100) * (n - 1) + 1;
    lo = min(max(floor(h), 1), n);
    hi = min(max(ceil(h), 1), n);
    y = x(lo) + (h - lo) * (x(hi) - x(lo));
end
