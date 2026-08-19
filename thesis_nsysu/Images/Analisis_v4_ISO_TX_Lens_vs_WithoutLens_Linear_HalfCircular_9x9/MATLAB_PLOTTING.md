# Plotting Figure dengan MATLAB

Script MATLAB membaca CSV hasil analisis yang sudah tersedia. Simulasi Sionna RT tidak dijalankan ulang.

## Menjalankan

Dari MATLAB Desktop, arahkan Current Folder ke root repository lalu jalankan:

```matlab
run('Analisis_v4_ISO_TX_Lens_vs_WithoutLens_Linear_HalfCircular_9x9/plot_analysis_figures_matlab.m')
```

Script juga dapat dijalankan dari folder lain karena seluruh path data dan output diselesaikan relatif terhadap lokasi script.

## Perilaku figure

- Delapan window figure dibuat dengan `Visible='on'`.
- Window tidak ditutup setelah proses ekspor, sehingga dapat di-zoom, diperiksa, atau disunting di MATLAB Desktop.
- Setiap figure disimpan sebagai PNG 180 dpi dan MATLAB `.fig` pada folder `figures_matlab/`.
- Data berasal dari CSV pada folder `data/`; tidak ada angka hasil simulasi yang di-hardcode ke plot, kecuali geometri TX 9-elemen dengan spacing 0,45 m yang merupakan konfigurasi identik keempat notebook.

## Daftar keluaran

1. `01_geometry_and_arrays_matlab`
2. `02_static_rx_scenario_comparison_matlab`
3. `03_static_mimo_comparison_matlab`
4. `04_channel_metrics_along_trajectory_matlab`
5. `05_trajectory_mimo_metrics_matlab`
6. `06_spatial_decorrelation_comparison_matlab`
7. `07_raw_spatial_difference_power_matlab`
8. `08_aggregate_comparison_matlab`

Setiap nama di atas mempunyai versi `.png` dan `.fig`.

Catatan: jika dijalankan memakai `matlab -batch`, figure tetap dirender dan disimpan, tetapi aplikasi MATLAB akan keluar setelah script selesai. Untuk mempertahankan window di layar, jalankan melalui MATLAB Desktop.
