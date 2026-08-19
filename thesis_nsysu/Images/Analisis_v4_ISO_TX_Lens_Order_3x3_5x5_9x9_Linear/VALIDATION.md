# Validation Report

## Overall Assessment: Share with caveats

## Methodology Review

Ketiga notebook diverifikasi berakhir pada Section 14. Analisis merekonsiliasi konfigurasi TX ISO, jumlah TX/RX, waypoint, link summary, MIMO trajectory, dan spatial metrics. Perbandingan diposisikan sebagai skalabilitas konfigurasi, bukan efek kausal tunggal dari order.

## Issues Found

Tidak ada kegagalan pemeriksaan otomatis.

- **High:** total daya nominal tidak konstan karena 10 dBm diterapkan per TX.
- **Medium:** sudut RX dan jumlah RX berbeda antar-order.
- **Medium:** matriks MIMO dibentuk dari simulasi RX N×1 berurutan.
- **Medium:** tidak ada multi-seed/convergence test dan hanya 100.000 path samples/source.
- **Low:** outage threshold 1 bit/s/Hz jenuh pada 0%.

## Calculation Spot-Checks

- Row trajectory RX: 21×3=63, 21×5=105, dan 21×9=189 diverifikasi.
- `correlation + decorrelation = 1` diperiksa untuk pooled dan median tables.
- Median/max trajectory MIMO dihitung ulang dari 21 waypoint per order.
- Effective rank diuji berada pada rentang 1 sampai N.
- TX pattern `iso` dan jumlah elemen 3/5/9 diverifikasi dari konfigurasi.
- TX spatial terpilih diverifikasi sebagai elemen tengah: indeks 1/2/4 untuk order 3/5/9.
- Signature seluruh PNG sumber Sections 11–14 diperiksa.

## Visualization Review

Delapan figure komparatif diperiksa dengan skala, unit, warna, marker, dan line style konsisten. Pita pada grafik link adalah rentang minimum–maksimum antar-RX, bukan confidence interval.

## Suggested Improvements

1. Jalankan eksperimen constant-total-power.
2. Samakan grid RX dan pertahankan pemilihan TX tengah pada semua order.
3. Tambahkan multi-seed dan sweep path samples.
4. Gunakan threshold outage yang lebih diskriminatif.

## Required Caveats for Stakeholders

- Kenaikan kapasitas absolut tercampur dengan kenaikan total daya dan dimensi matriks.
- Spatial result kini memakai TX tengah pada semua order, tetapi grid RX masih berbeda.
- Hasil bersifat deskriptif untuk satu scene dan output tersimpan.
- Tidak ada Section 15 dalam cakupan laporan.
