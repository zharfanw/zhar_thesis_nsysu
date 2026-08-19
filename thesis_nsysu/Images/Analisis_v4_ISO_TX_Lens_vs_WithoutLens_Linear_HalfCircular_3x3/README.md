# Artefak Analisis v4 3-TX ISO

Laporan utama: [ANALISIS.md](ANALISIS.md). Analisis hanya mencakup Sections 1–14.

- `data/`: CSV terstruktur, summary, dan delta Lens.
- `figures/`: delapan figure komparatif serta figure sumber Sections 11–14.
- `figures_matlab/`: delapan figure MATLAB dalam format PNG dan `.fig` yang dapat diedit.
- `metadata/`: provenance, hash, inventaris, chart map, data dictionary, dan validasi.
- `build_analysis.py`: script reproduksi dari output notebook tersimpan.
- `plot_analysis_figures_matlab.m`: script MATLAB yang membaca CSV hasil ekstraksi.
- `MATLAB_PLOTTING.md`: petunjuk menjalankan dan membuka figure MATLAB.

```powershell
conda activate sionna_env
python Analisis_v4_ISO_TX_Lens_vs_WithoutLens_Linear_HalfCircular_3x3/build_analysis.py
```

Figure MATLAB dapat dibangun ulang dari root repository:

```matlab
run('Analisis_v4_ISO_TX_Lens_vs_WithoutLens_Linear_HalfCircular_3x3/plot_analysis_figures_matlab.m')
```
