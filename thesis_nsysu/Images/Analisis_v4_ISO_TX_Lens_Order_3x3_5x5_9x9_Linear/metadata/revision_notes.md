# Revision Notes

Revisi ini dibuat setelah `SPATIAL_DECORR_TX_INDEX` pada notebook 5×5 diubah dari `4` menjadi `2` dan Sections 12–14 dijalankan ulang.

## Perubahan metrik 5×5

| Metrik | Sebelum (TX 4, tepi) | Sesudah (TX 2, tengah) | Delta |
| --- | ---: | ---: | ---: |
| Pooled correlation | 0.0695 | 0.0724 | +0.0029 |
| Pooled decorrelation | 0.9305 | 0.9276 | -0.0029 |
| Median correlation | 0.4281 | 0.4834 | +0.0553 |
| Median decorrelation | 0.5719 | 0.5166 | -0.0553 |
| Raw cross-correlation | 1.497993e-09 | 1.761312e-09 | +2.633190e-10 |
| Raw difference power | 3.737515e-08 | 4.204834e-08 | +4.673190e-09 |

Secara metodologis, `SPATIAL_DECORR_TX_INDEX` hanya digunakan oleh Sections 12–14. Output tersimpan Section 11 pada notebook terbaru juga mengalami perubahan numerik sangat kecil (sekitar 5×10⁻⁴ bit/s/Hz pada median MIMO capacity), kemungkinan karena cell simulasi ikut dijalankan ulang; laporan memakai seluruh output terbaru tersebut.
