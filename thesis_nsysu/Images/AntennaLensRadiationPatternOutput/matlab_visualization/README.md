# MATLAB Antenna-Lens Visualizations

Paket ini membaca data yang diekspor oleh
`AntennaLensRadiationPattern.ipynb`, menampilkan seluruh plot, dan menyimpan
gambar hasil MATLAB ke folder `figures/`.

Visualisasi yang tersedia:

1. Ringkasan directivity, gain, efficiency, dan peak direction.
2. Vertical cut 360° pada bidang X-Z.
3. Horizontal cut 360° pada bidang X-Y.
4. Cut 360° pada bidang Y-Z.
5. Geometri akuisisi transmitarray 3D.
6. Radiation pattern 3D untuk seluruh pola unik.

## Menjalankan semuanya

Buka MATLAB, pindah ke folder ini, lalu jalankan:

```matlab
run_all_visualizations
```

Atau dari root repository:

```matlab
run("AntennaLensRadiationPatternOutput/matlab_visualization/run_all_visualizations.m")
```

Setiap fungsi `plot_*.m` juga dapat dijalankan secara terpisah.

Jika folder `data/` belum tersedia, jalankan notebook
`AntennaLensRadiationPattern.ipynb` dari awal sampai selesai terlebih dahulu.
