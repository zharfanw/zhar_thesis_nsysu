# Validation Report

## Overall Assessment: Share with caveats

## Methodology Review

Empat notebook berhasil dibaca hingga cell terakhir dan semuanya berakhir pada Section 14. Parameter inti, jumlah TX/RX, frequency bins, waypoint, sampling mobilitas, dan link budget direkonsiliasi. Hasil disajikan sebagai perbandingan desain sistem, bukan klaim kausal murni efek material Lens.

## Issues Found

Tidak ada kegagalan pemeriksaan otomatis.

- **Medium:** geometri dan pola RX berbeda antara Lens dan Without Lens.
- **Medium:** MIMO 9×9 dibentuk dari simulasi RX berurutan, bukan semua RX aktif simultan.
- **Medium:** tidak ada multi-seed/convergence test dan hanya 100.000 path samples/source.
- **Low:** outage threshold 1 bit/s/Hz jenuh pada 0%.

## Calculation Spot-Checks

- 21×9=189 baris linear dan 37×9=333 baris half-circular diverifikasi.
- Outage dari log waypoint direkonsiliasi dengan summary notebook.
- Identitas `correlation + decorrelation = 1` diuji pada pooled dan median tables.
- Median trajectory MIMO dihitung ulang langsung dari seluruh baris waypoint.
- Konfigurasi TX diverifikasi `TX_PATTERN_MODE=iso` dan memiliki sembilan posisi.
- Signature seluruh PNG sumber Sections 11–14 diperiksa.

## Visualization Review

Semua figure memakai warna, line style, marker, unit, dan skala yang konsisten dalam panel sebanding. Pita pada grafik kanal adalah rentang minimum–maksimum antar-RX, bukan confidence interval.

## Suggested Improvements

1. Uji practical beam-selection agar directional Lens dinilai sesuai mode operasionalnya.
2. Gunakan koordinat RX identik untuk mengisolasi efek pola Lens.
3. Lakukan multi-seed dan sweep 1.000.000 path samples/source.
4. Gunakan threshold outage tambahan 5/6 bit/s/Hz dan laporkan percentile.

## Required Caveats for Stakeholders

- Hasil bersifat deskriptif untuk satu scene simulasi.
- MIMO trajectory adalah konstruksi dari sembilan simulasi 9×1.
- Tidak ada Section 15 dalam cakupan atau artefak laporan.
