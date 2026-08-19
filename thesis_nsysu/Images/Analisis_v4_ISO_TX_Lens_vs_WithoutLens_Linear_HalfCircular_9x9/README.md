# Artefak Analisis v4 9-TX ISO

Laporan utama: [ANALISIS.md](ANALISIS.md). Analisis hanya mencakup Sections 1–14.

- `data/`: CSV terstruktur, summary, dan delta Lens.
- `figures/`: eight English-language comparative figures plus original source figures from Sections 11–14.
- `figures_matlab/`: English-language MATLAB outputs in PNG and editable `.fig` formats.
- `metadata/`: provenance, hash, inventaris, chart map, data dictionary, dan validasi.
- `build_analysis.py`: script reproduksi dari output notebook tersimpan.
- `plot_analysis_figures_matlab.m`: displays and saves all eight English-language MATLAB figures.
- [MATLAB_PLOTTING.md](MATLAB_PLOTTING.md): MATLAB usage instructions and output list.

```powershell
conda activate sionna_env
python Analisis_v4_ISO_TX_Lens_vs_WithoutLens_Linear_HalfCircular_9x9/build_analysis.py
```

Run the MATLAB version from MATLAB Desktop:

```matlab
run('Analisis_v4_ISO_TX_Lens_vs_WithoutLens_Linear_HalfCircular_9x9/plot_analysis_figures_matlab.m')
```
