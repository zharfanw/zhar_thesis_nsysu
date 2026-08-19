# Analisis v4 Lens Order 3×3, 5×5, dan 9×9

Laporan utama: [ANALISIS.md](ANALISIS.md). Cakupan hanya Sections 1–14.

- `data/`: CSV per order dan gabungan.
- `figures/`: eight English-language comparative figures plus original source figures from Sections 11–14.
- `figures_matlab/`: English-language MATLAB outputs in PNG and editable `.fig` formats.
- `metadata/`: provenance, data dictionary, chart map, inventaris, dan validasi.
- `metadata/revision_notes.md`: perubahan hasil setelah TX spatial 5×5 diperbaiki dari indeks 4 ke 2.
- `build_analysis.py`: generator reproducible dari output notebook tersimpan.
- `plot_analysis_figures_matlab.m`: displays and saves all eight English-language MATLAB figures.
- [MATLAB_PLOTTING.md](MATLAB_PLOTTING.md): MATLAB usage instructions and output list.

```powershell
conda activate sionna_env
python Analisis_v4_ISO_TX_Lens_Order_3x3_5x5_9x9_Linear/build_analysis.py
```

Run the MATLAB version from MATLAB Desktop:

```matlab
run('Analisis_v4_ISO_TX_Lens_Order_3x3_5x5_9x9_Linear/plot_analysis_figures_matlab.m')
```
