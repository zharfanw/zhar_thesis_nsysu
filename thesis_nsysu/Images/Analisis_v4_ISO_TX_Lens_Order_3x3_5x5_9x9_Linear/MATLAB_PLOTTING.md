# Plot Figure dengan MATLAB

Script utama: [`plot_analysis_figures_matlab.m`](plot_analysis_figures_matlab.m).

Script membaca CSV yang sudah tersedia pada `data/`; Sionna RT dan notebook tidak dijalankan ulang. Delapan figure akan:

1. ditampilkan sebagai window MATLAB dengan `Visible='on'`;
2. tetap terbuka setelah script selesai;
3. disimpan sebagai PNG beresolusi 180 dpi;
4. disimpan sebagai `.fig` agar dapat diedit kembali di MATLAB.

## Menjalankan dari MATLAB Desktop

Buka MATLAB, arahkan Current Folder ke root repository, lalu jalankan:

```matlab
run('Analisis_v4_ISO_TX_Lens_Order_3x3_5x5_9x9_Linear/plot_analysis_figures_matlab.m')
```

Script menggunakan lokasi filenya sendiri untuk menemukan CSV, sehingga juga dapat dibuka dan dijalankan langsung melalui tombol **Run** di MATLAB Editor.

## Output

Output disimpan pada folder:

```text
figures_matlab/
├── 01_geometry_order_comparison_matlab.png/.fig
├── 02_static_rx_by_order_matlab.png/.fig
├── 03_static_mimo_scaling_matlab.png/.fig
├── 04_channel_along_trajectory_matlab.png/.fig
├── 05_trajectory_mimo_scaling_matlab.png/.fig
├── 06_spatial_decorrelation_by_order_matlab.png/.fig
├── 07_raw_spatial_difference_by_order_matlab.png/.fig
└── 08_aggregate_order_comparison_matlab.png/.fig
```

MATLAB R2019b atau lebih baru direkomendasikan karena script menggunakan `tiledlayout` dan `exportgraphics`. Script telah divalidasi dengan MATLAB R2023b.
