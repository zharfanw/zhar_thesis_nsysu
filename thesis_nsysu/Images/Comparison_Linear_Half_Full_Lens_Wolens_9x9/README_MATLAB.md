# MATLAB Figure Generator

Jalankan file `generate_all_figures.m` menggunakan MATLAB dari direktori mana pun.
Script akan membaca CSV pada folder `data/` dan menyimpan hasil ke folder
`matlab_figures/` dalam format `.fig` dan `.png`.

Figure yang dihasilkan:

1. `01_geometry_six_scenarios`
2. `02_linear_all_parameters`
3. `02_half_all_parameters`
4. `02_full_all_parameters`
5. `05_aggregate_comparison`

Raw cross-correlation dan raw difference power tetap berasal dari data tanpa
normalisasi. Skala log hanya digunakan untuk menampilkan rentang nilainya.

Disarankan MATLAB R2020a atau lebih baru karena script menggunakan
`tiledlayout`, string array, `MarkerIndices`, dan `exportgraphics`.
