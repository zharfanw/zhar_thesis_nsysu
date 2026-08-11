% RUN_ALL_VISUALIZATIONS Display and save every exported antenna visualization.

clear;
close all;
clc;

packageDirectory = fileparts(mfilename("fullpath"));
addpath(packageDirectory);

fprintf("Running all antenna-lens visualizations...\n\n");

plot_pattern_summary();
plot_vertical_cut_360();
plot_horizontal_cut_360();
plot_yz_cut_360();
plot_transmitarray_geometry_3d();
plot_radiation_pattern_3d();

paths = visualization_paths();
fprintf("\nAll visualizations completed.\n");
fprintf("Saved MATLAB figures: %s\n", paths.figures);
