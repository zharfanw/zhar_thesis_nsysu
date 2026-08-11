# Full 360° Vertical-Cut Output

Folder ini menyimpan hasil ekspor dari bagian **6a** pada
`AntennaLensRadiationPattern.ipynb`.

- `data/vertical_cut_360_all_patterns.csv`: data gabungan seluruh pola.
- `data/*_vertical_cut_360.csv`: data setiap pola.
- `figures/vertical_cut_360_all_patterns.png`: grafik gabungan.
- `figures/*_vertical_cut_360.png`: grafik setiap pola.
- `show_vertical_cut_360.py`: menampilkan tabel lengkap, menggambar ulang grafik,
  dan menyimpan hasilnya.

Jalankan script dari root project:

```powershell
conda activate sionna_env
python AntennaLensRadiationPatternOutput/vertical_cut_360/show_vertical_cut_360.py
```
