# Data Dictionary

- `comparison_summary.csv`: headline per order, termasuk metrik absolut dan ternormalisasi.
- `order_effects.csv`: delta 3×3→5×5, 5×5→9×9, dan 3×3→9×9.
- `simulation_parameters.csv`: parameter konfigurasi dan invariant TX ISO.
- `static_summary_combined.csv`: gain, korelasi TX, dan capacity Section 9.
- `rx_summary_combined.csv`: median/min/outage per RX sepanjang trajectory.
- `waypoint_samples_combined.csv`: SNR dan capacity log per waypoint × RX.
- `trajectory_mimo_combined.csv`: condition number, effective rank, capacity per waypoint.
- `spatial_pooled/raw/median_combined.csv`: output Sections 12–14.

Versi per order menggunakan prefix `order_3x3`, `order_5x5`, atau `order_9x9`.
