# Analisis Skalabilitas Monte Carlo (v3, konsisten) — N = 3×3, 5×5, 9×9

Folder khusus untuk analisis perbandingan **skalabilitas** metode Monte Carlo (Random-TX, section 11 pada notebook) antara tiga ukuran array TX/skenario-RX: **N = 3, 5, 9** — kali ini **ketiganya dari notebook "v3"** yang konsisten (bukan campuran v2/v3).

Ini adalah **versi perbaikan** dari analisis sebelumnya di
[`../Analisis_Skalabilitas_MonteCarlo_3x3_5x5_9x9/`](../Analisis_Skalabilitas_MonteCarlo_3x3_5x5_9x9/),
yang memakai notebook **"v2"** untuk N=5 dan ternyata mengandung bug konversi radian ganda pada orientasi RX (lihat dokumen pembahasan lama untuk detail bug). Di sini, N=5 memakai
`Setupv3_20mx20m_lens_5x5_Patch_randomCom.ipynb`, yang sudah diverifikasi memakai literal derajat langsung untuk `rx_orientation_deg` (pola yang sama seperti v3 3x3/9x9) — bebas dari bug tersebut.

Dokumen pembahasan lengkap (naratif, tabel, dan kesimpulan) ada di root repo:
[`../ANALISIS_SKALABILITAS_MONTE_CARLO_v3_3x3_5x5_9x9.md`](../ANALISIS_SKALABILITAS_MONTE_CARLO_v3_3x3_5x5_9x9.md).

## Sumber

| N | Notebook |
|---|---|
| 3 | [`Setupv3_20mx20m_lens_3x3_Patch_randomCom.ipynb`](../Setupv3_20mx20m_lens_3x3_Patch_randomCom.ipynb) |
| 5 | [`Setupv3_20mx20m_lens_5x5_Patch_randomCom.ipynb`](../Setupv3_20mx20m_lens_5x5_Patch_randomCom.ipynb) |
| 9 | [`Setupv3_20mx20m_lens_9x9_Patch_randomCom.ipynb`](../Setupv3_20mx20m_lens_9x9_Patch_randomCom.ipynb) |

Ketiga notebook **tidak dieksekusi ulang**. Seluruh angka diambil dari output sel yang sudah tersimpan (lihat `data/raw_logs/`), lalu diparse menjadi CSV (`data/`) dan diplot (`figures/`) oleh `scripts/build_comparison.py`.

## Isi folder

```
data/
  raw_logs/*_key_cells_output.txt          teks mentah verbatim dari sel 11, 30/33, 36, 39, 43, 48, 50
  mimo_fixed_geometry_by_N.csv             sec. 10 -- cond. number, effective rank, kapasitas @10dB
  rx_spatial_correlation_by_N.csv          sec. 10b -- korelasi spasial sisi-RX
  best_scenario_fixed_geometry_by_N.csv    sec. 9 -- skenario combined-gain terbaik per N
  montecarlo_aggregate_by_N.csv            sec. 11 -- ringkasan agregat (median/p05/p95, throughput, delay spread)
  montecarlo_per_rx_scenario_by_N.csv      sec. 11 -- rincian per skenario sudut lensa
  montecarlo_mimo_per_drop_summary_by_N.csv sec. 11c -- ringkasan median atas 20 drop
  montecarlo_mimo_per_drop_raw_N3_N5_N9.csv sec. 11c -- 60 baris mentah (20 drop x 3 N), utuh
  compute_cost_by_N.csv                    jumlah panggilan PathSolver (aktual vs skema naif)
figures/
  fig1_compute_cost_scalability.png
  fig2_mimo_fixed_geometry_vs_N.png
  fig3_rx_correlation_vs_N.png
  fig4_montecarlo_aggregate_vs_N.png
  fig5_mimo_per_drop_boxplot_vs_N.png
scripts/
  build_comparison.py                      generate seluruh CSV + PNG di atas dari angka bersumber notebook
```

Untuk membuat ulang CSV dan figure (butuh `pandas`, `numpy`, `matplotlib` -- tersedia di env `sionna_env`):

```bash
cd scripts
python build_comparison.py
```
