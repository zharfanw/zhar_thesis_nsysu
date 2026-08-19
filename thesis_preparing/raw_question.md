Abstrak menyebut eksperimen \(3\times3\), tetapi kesimpulan menyebut \(9\times9\). Mana hasil yang benar?
Arah jawaban: Menurut Bab 3 aktif, eksperimen lens versus without-lens adalah \(3\times3\). Angka yang konsisten adalah link capacity 5.41→3.57 bit/s/Hz untuk linear dan 5.08→3.53 untuk half-circular. Constructed-MIMO capacity berubah 6.12→5.85 dan 6.71→6.58. Angka \(9\times9\) di Bab 4 berasal dari versi analisis sebelumnya dan harus disinkronkan.

Judul menyatakan “spatial multiplexing enhancement”, tetapi hasil sistem menunjukkan kapasitas dan effective rank justru menurun. Apakah judul Anda overclaim?
Arah jawaban: Enhancement yang terbukti bersifat kondisional, bukan universal. Lensa meningkatkan angular selectivity dan local decorrelation, tetapi equal weighting terhadap semua branch—termasuk yang tidak sejajar—menurunkan median kapasitas. Keuntungan sistem memerlukan beam selection atau combining yang belum diuji. Jika judul masih dapat diubah, kata “evaluation” lebih defensible daripada menjanjikan enhancement secara umum.

Apa novelty tesis ini jika unit-cell topology, antenna lens 38 GHz, dan beamspace MIMO sudah pernah diteliti?
Arah jawaban: Novelty bukan unit cell baru atau lensa 38 GHz pertama. Kontribusi yang defensible adalah integrasi nonidealitas physical transmitarray \(20\times20\) dengan evaluasi matriks MIMO, pemisahan raw link gain dari normalized spatial structure, cross-solver verification, serta pembuktian bahwa focusing tidak otomatis menghasilkan system-level multiplexing gain.

Target focal distance adalah 30 mm, tetapi hasilnya 14 mm—error 53.3%. Bagaimana desain ini dapat disebut berhasil?
Arah jawaban: Desain berhasil menghasilkan localized focus dan focal arc, tetapi tidak berhasil memenuhi target focal distance. Phase quantization mungkin berkontribusi, tetapi belum terbukti sebagai satu-satunya penyebab. Kemungkinan lain ialah cakupan fase tidak penuh, variasi amplitudo, mutual coupling, oblique incidence, finite aperture, dan feed phase-center error.

Mengapa Anda mengatribusikan focal shift kepada phase quantization tanpa ablation study?
Arah jawaban: Klaim yang aman adalah focal shift “consistent with aggregate phase-realization errors”, bukan disebabkan secara eksklusif oleh quantization. Pembuktian memerlukan perbandingan ideal continuous-phase sheet, quantized ideal sheet, dan full physical array.

Library hanya menyediakan sekitar \(258^\circ\) phase coverage dan menerima \(S_{21}>-5\) dB. Apakah itu cukup untuk disebut lensa yang efisien?
Arah jawaban: \(-5\) dB hanya menjamin lebih dari 31.6% daya diteruskan. Itu merupakan design trade-off, bukan bukti efisiensi tinggi. Jumlah 324 geometri juga tidak berarti terdapat 324 phase states yang benar-benar berbeda. Seharusnya dilaporkan RMS phase error, amplitude uniformity, aperture efficiency, reflection, loss, dan jumlah phase state efektif.

Apakah periodic unit-cell simulation pada normal incidence valid untuk seluruh aperture?
Arah jawaban: Hanya sebagai pendekatan desain awal. Dengan aperture 44.24 mm dan target fokus 30 mm, sudut lokal pada sudut aperture dapat mencapai sekitar \(46^\circ\); terhadap fokus aktual 14 mm dapat mendekati \(66^\circ\). Karena itu, sel tepi mengalami kondisi yang jauh dari normal incidence dan locally periodic approximation menjadi lemah.

Bisakah lensa pasif menciptakan degree of freedom atau rank kanal yang sebelumnya tidak ada?
Arah jawaban: Tidak. Untuk transformasi pasif linear,
\[
\mathbf H_{\mathrm{eff}}=\mathbf B\mathbf H_{\mathrm{prop}}\mathbf A,
\qquad
\operatorname{rank}(\mathbf H_{\mathrm{eff}})
\leq \operatorname{rank}(\mathbf H_{\mathrm{prop}}).
\]Lensa hanya memetakan dan membantu receiver mengakses angular modes yang sudah ada; ia tidak menciptakan propagation paths baru.

Apakah HFSS SBR+, HFSS Hybrid, dan Sionna-RT benar-benar tiga validasi independen?
Arah jawaban: Tidak sepenuhnya. SBR+ dan Hybrid berbagi propagation engine SBR+, sedangkan Sionna-RT menggunakan radiation pattern yang berasal dari HFSS. Ini lebih tepat disebut cross-tool numerical verification atau qualitative triangulation, bukan experimental validation.

Mengapa 25 dari 27 titik atau 92.6% disebut bukti kuat? Apakah 27 titik itu independen?
Arah jawaban: Nilai tersebut hanya descriptive sign agreement. Link dan titik frekuensi berbagi geometri serta kondisi propagasi sehingga tidak independen. Angka 92.6% mendukung konsistensi kualitatif, tetapi bukan statistical significance.

Bagaimana S-parameter HFSS dapat dibandingkan dengan CFR Sionna-RT?
Arah jawaban: Keduanya dapat disusun menggunakan indeks matriks \(\mathbf H\) yang sama, tetapi tidak identik secara absolut. S-parameter memasukkan port normalization, mismatch, coupling, antenna, dan reference plane; CFR Sionna berasal dari coherent path coefficients dan imported patterns. Karena itu, perbandingan paling kuat adalah arah perubahan dan normalized structure, bukan kesamaan nilai absolut.

Apa arti sebenarnya dari Frobenius-normalized capacity? Apakah itu achievable throughput?
Arah jawaban: Bukan. Normalisasi menghilangkan perbedaan total channel energy sehingga kapasitas tersebut hanya menilai bentuk singular-value spectrum. Ia merupakan channel-structure metric, bukan kapasitas link fisik dan bukan formal multiplexing gain.

Apa persamaan normalisasi yang digunakan untuk constructed-MIMO capacity pada 10 dB di Bab 3?
Arah jawaban: Ini harus dijelaskan secara eksplisit. Jika memakai unit-Frobenius normalization seperti Bab 2, kapasitas maksimum \(3\times3\) pada total SNR 10 dB hanya sekitar 3.23 bit/s/Hz, sedangkan hasil Bab 3 mencapai 5.85–7.24. Berarti normalisasinya berbeda. Jangan menyebutnya Frobenius normalization sebelum formula scaling yang sebenarnya dipastikan dari source workflow.

Anda menyebut raw capacity pada “20 dB”, tetapi nilainya hanya sekitar 0.3–1.4 bit/s/Hz. Di mana SNR 20 dB tersebut didefinisikan?
Arah jawaban: \(\rho=100\) adalah reference atau pre-channel SNR dalam formula. Karena raw \(\mathbf H\) masih memuat path loss, effective post-channel eigenmode SNR dapat jauh lebih kecil. Istilah “20 dB SNR” harus disertai reference plane agar tidak dianggap received SNR.

Apakah matriks \(N\times N\) yang dibentuk dari beberapa simulasi \(N\times1\) secara berurutan benar-benar merupakan kanal MIMO simultan?
Arah jawaban: Tidak sepenuhnya. Matriks tersebut adalah constructed channel-structure diagnostic. Ia tidak memodelkan simultaneous reception, mutual coupling antarport, common hardware phase, correlated receiver noise, switching overhead, atau joint combining. Validitasnya juga mensyaratkan reference phase antar-run konsisten.

Dalam link capacity, tiga TX digabung secara non-coherent. Apakah ketiga TX mengirim sinyal yang sama, orthogonal, atau independent streams?
Arah jawaban: Asumsi sinyal harus diperjelas. Jika mengirim waveform yang sama, medan seharusnya dijumlahkan secara coherent. Jika independent cochannel streams, diperlukan model interference atau MIMO detector. Penjumlahan daya dan \(\log_2(1+\sum\gamma_i)\) paling sesuai apabila kontribusinya orthogonal atau diperlakukan sebagai total desired energy.

Bisakah perbedaan hasil diatribusikan kepada lensa, padahal posisi RX dan radiation pattern berubah bersamaan?
Arah jawaban: Tidak secara kausal. Baseline memakai array linear 11.06 mm dengan pola patch yang sama, sedangkan lens case memakai focal arc sekitar 24.04 mm dan pola \(+45^\circ,0^\circ,-45^\circ\). Hasil yang sah adalah perbandingan dua complete receiver designs, bukan efek material lensa saja.

Mengapa global decorrelation hampir sempurna, tetapi local block decorrelation sangat rendah pada baseline?
Arah jawaban: Global estimator menggabungkan waypoint, waktu, dan frekuensi sebelum normalisasi. Perubahan fase sepanjang trajectory dapat saling membatalkan sehingga respons tampak tidak berkorelasi secara global. Block median mengukur kondisi lokal yang dialami receiver secara bersamaan dan karena itu menjawab pertanyaan berbeda.

Bagaimana condition number dapat membaik, tetapi effective rank dan capacity menurun?
Arah jawaban: Condition number hanya menggunakan \(\sigma_1/\sigma_N\), sedangkan effective rank dan capacity menggunakan seluruh singular-value spectrum. Selain itu, median setiap metrik belum tentu berasal dari waypoint yang sama. Karena itu, satu metrik tidak cukup untuk menyimpulkan multiplexing advantage.

Apakah peningkatan capacity \(3\times3\rightarrow9\times9\) sebesar 148.9% membuktikan manfaat causal dari MIMO order?
Arah jawaban: Tidak. Total TX power naik 4.77 dB, aperture membesar dari 0.90 menjadi 3.60 m, dan RX angle grid berubah. Pada 38 GHz, spacing 0.45 m sekitar \(57\lambda\), sehingga sistem lebih menyerupai distributed or macro-scale MIMO daripada compact array. Kesimpulan yang sah hanya configuration-level scaling.

Apakah penurunan constructed-MIMO capacity sebesar 0.13–0.27 bit/s/Hz benar-benar signifikan?
Arah jawaban: Belum dapat dibuktikan. Penelitian hanya memakai satu scene, satu stored realization, tanpa multi-seed confidence interval dan tanpa convergence sweep. Run menggunakan 100,000 path samples per source, sedangkan workflow merekomendasikan 1,000,000.

Anda mengatakan beam selection dapat mengubah selectivity menjadi keuntungan sistem. Di mana hasil eksperimennya?
Arah jawaban: Belum ada; itu merupakan future-work hypothesis. Jangan menyatakan bahwa beam selection pasti menghasilkan net gain sebelum memperhitungkan training, switching, alignment error, dan combining loss.

Berikut pembahasan dan jawaban yang aman untuk delapan pertanyaan tersebut.
1. Mengapa decorrelation hanya dihitung dari center TX?
Center TX dipilih karena merupakan referensi yang sama dan paling simetris untuk konfigurasi \(3\times3\), \(5\times5\), dan \(9\times9\). Dengan begitu, analisis difokuskan pada perbedaan respons antar-RX akibat posisi dan pola sudutnya.
Namun, hasil tersebut tidak mewakili decorrelation seluruh kanal MIMO. Pemilihan center TX juga bisa bias karena arah ini biasanya paling sesuai dengan boresight lensa.
Jawaban sidang:
Center TX digunakan sebagai reference illumination yang tersedia pada semua order dan paling simetris terhadap lensa. Namun, metrik tersebut hanya mengukur RX-response diversity untuk satu arah datang. Karena itu, saya tidak menyamakannya dengan decorrelation seluruh matriks MIMO. Evaluasi yang lebih lengkap harus menghitung decorrelation untuk setiap TX, kemudian melaporkan distribusi atau rata-ratanya.

Perbaikannya adalah menghitung
\[
\overline D=
\frac{1}{N_T}
\sum_{j=1}^{N_T}
\frac{1}{\binom{N_R}{2}}
\sum_{i<k}\left(1-\left|\rho_{ik}^{(j)}\right|\right).
\]2. Mengapa menggunakan istilah “ergodic capacity” tanpa banyak independent channel realizations?
Untuk satu matriks \(\mathbf H(f)\), persamaan
\[
C=\log_2\det\left(
\mathbf I+\frac{\rho}{N_T}\mathbf H\mathbf H^H
\right)
\]adalah instantaneous channel capacity atau instantaneous mutual information.
Jika hasil dirata-ratakan terhadap 401 frequency bins, istilah yang lebih tepat adalah frequency-averaged capacity. Ia baru dapat disebut ergodic capacity apabila averaging dilakukan terhadap distribusi random channel yang representatif, misalnya banyak independent drops, posisi, atau seed, dengan asumsi ergodicity.
Jawaban sidang:
Istilah ergodic capacity pada bagian tersebut kurang tepat. Untuk setiap matriks kanal, yang dihitung adalah instantaneous capacity. Pada trajectory study terdapat averaging terhadap frekuensi, sehingga lebih tepat disebut frequency-averaged ideal capacity. Karena penelitian ini tidak memiliki banyak independent random realizations, saya tidak mengklaim bahwa nilainya merupakan ergodic capacity populasi.

3. Mengapa outage threshold 1 bit/s/Hz tetap digunakan jika semuanya menghasilkan 0% outage?
Threshold tersebut kemungkinan digunakan sebagai reference atau sanity check dari source workflow. Masalahnya, karena semua konfigurasi menghasilkan 0% outage, metrik tersebut sudah saturated dan tidak mempunyai daya pembeda.
Jawaban sidang:
Threshold 1 bit/s/Hz dipertahankan sebagai reference awal, tetapi hasil 0% pada semua konfigurasi menunjukkan bahwa threshold itu tidak informatif untuk skenario ini. Karena itu, saya tidak menggunakan hasil tersebut sebagai bukti reliability advantage.

Analisis yang lebih baik adalah:
kapasitas persentil ke-5 atau ke-10;
kurva CDF kapasitas;
outage-versus-rate curve;
threshold yang lebih relevan, misalnya 3–6 bit/s/Hz;
threshold berdasarkan target modulation and coding scheme.
4. Apakah 401 frequency bins dan 16 time samples merupakan independent observations?
Tidak.
Untuk bandwidth 400 MHz dengan 401 bins, jarak antarbin kira-kira
\[
\Delta f=\frac{400\text{ MHz}}{400}=1\text{ MHz}.
\]Independensi frekuensi ditentukan oleh coherence bandwidth, yang bergantung pada RMS delay spread:
\[
B_c\approx\frac{1}{5\tau_{\mathrm{rms}}}.
\]Tanpa menghitung \(\tau_{\mathrm{rms}}\) dari CIR, tidak dapat diketahui berapa bin yang efektif independen. Adjacent bins yang hanya berjarak 1 MHz kemungkinan berkorelasi.
Untuk domain waktu:
\[
\lambda=\frac{c}{38\text{ GHz}}\approx7.89\text{ mm}.
\]Dengan kecepatan 1 m/s:
\[
f_D\approx\frac{v}{\lambda}\approx127\text{ Hz},
\qquad
T_c\approx\frac{0.423}{f_D}\approx3.3\text{ ms}.
\]Karena time sampling dilakukan setiap 1 ms, adjacent samples kemungkinan masih berkorelasi. Enam belas samples bukan berarti terdapat 16 independent trials.
Jawaban sidang:
Frequency bins dan time samples saya perlakukan sebagai structured channel samples, bukan independent Monte Carlo trials. Independensi sebenarnya harus diperiksa melalui delay spread, coherence bandwidth, Doppler spectrum, dan temporal autocorrelation. Karena itu, jumlah bins atau time samples tidak digunakan sebagai ukuran statistical sample size.

5. Berapa aperture efficiency, beamwidth, sidelobe, cross-polarization, dan insertion loss?
Sebagian besar parameter tersebut belum dihitung secara eksplisit dalam tesis.
Jika aperture benar \(44.24\times44.24\) mm² dan peak realized gain benar sekitar 16 dBi, estimasi kasar aperture efficiency adalah
\[
\eta_{\mathrm{ap}}
=
\frac{G\lambda^2}{4\pi A}
\approx 10\%.
\]Untuk gain 12 dBi pada sudut lebar, nilainya kira-kira 4%. Tetapi estimasi ini hanya sah jika angka gain merupakan absolute realized gain dan ukuran aperture telah dikonfirmasi.
Beamwidth ideal aperture seragam secara kasar:
\[
\mathrm{HPBW}\approx0.886\frac{\lambda}{D}
\approx9^\circ,
\]tetapi actual beamwidth bisa lebih lebar karena illumination taper, phase error, dan incomplete phase coverage.
Jawaban sidang:
Tesis menunjukkan peak gain sekitar 16 dB pada boresight dan sekitar 12 dB pada sudut terlebar, serta peningkatan sidelobe pada wide-angle states. Namun, aperture efficiency, HPBW, sidelobe level, cross-polarization, dan complete lens insertion loss belum diekstrak secara sistematis. Nilai \(S_{21}>-5\) dB adalah kriteria unit cell, bukan insertion loss keseluruhan lensa.

Jangan mengarang nilai cross-polarization atau sidelobe level jika belum ada hasilnya.
6. Mengapa memilih 38 GHz dan bandwidth 400 MHz? Bagaimana dengan beam squint?
38 GHz dipilih karena:
berada pada wilayah mmWave/FR2 sekitar 37–40 GHz;
sesuai dengan desain patch dan unit-cell library;
menawarkan aperture elektrik yang cukup besar dalam ukuran fisik yang relatif kecil;
relevan untuk komunikasi broadband berarah.
Bandwidth 400 MHz memberikan fractional bandwidth:
\[
\frac{400\text{ MHz}}{38\text{ GHz}}\times100\%
\approx1.05\%.
\]Secara ideal, beam squint pada bandwidth ini mungkin tidak besar. Untuk arah sekitar \(60^\circ\), fixed-phase steering secara kasar dapat bergeser sekitar \(0.5^\circ\) dari center frequency ke salah satu band edge. Namun, metasurface dispersion dapat menyebabkan perubahan yang lebih besar pada fase, fokus, gain, dan sidelobe.
Jawaban sidang:
Bandwidth 400 MHz dipilih sebagai wideband communication channel di sekitar frekuensi desain 38 GHz dengan computational cost yang masih terkendali. Fractional bandwidth-nya sekitar 1.05%, tetapi saya belum melakukan quantitative beam-squint study. Karena unit cell bersifat dispersive, sensitivitas terhadap frekuensi harus diverifikasi menggunakan focal position dan radiation pattern pada beberapa frequency points, bukan hanya berdasarkan fractional bandwidth.

7. Bagaimana memastikan phase reference imported patterns konsisten antar-RX state?
Yang harus konsisten adalah:
phase center dan coordinate origin;
arah sumbu serta definisi \(\theta,\phi\);
polarization basis \(E_\theta,E_\phi\);
absolute-gain versus normalized-pattern convention;
reference plane;
frequency grid;
complex phase, bukan hanya magnitude gain.
Jika pattern yang diimpor hanya berupa gain magnitude, relative electromagnetic phase antarstate tidak dapat direkonstruksi sepenuhnya.
Jawaban sidang:
Konsistensi phase reference memerlukan seluruh pattern diekspor sebagai complex \(E_\theta\) dan \(E_\phi\) dengan coordinate origin, phase center, polarization basis, dan normalization yang identik. Selanjutnya diperlukan canonical LoS test untuk memastikan bahwa perubahan pattern rotation menghasilkan fase dan arah beam yang benar.

Constant phase offset pada satu RX row tidak mengubah singular values atau magnitude correlation. Namun, frequency-dependent phase offset, phase-center displacement, atau coordinate rotation yang salah dapat mengubah hasil constructed channel.
Kelemahan saat ini adalah complete complex CFR tensor dan source notebook tidak tersedia, sehingga phase consistency belum dapat diverifikasi end-to-end dari archive.
8. Apakah hasil tetap sama jika total TX power, aperture, dan RX angle set dibuat identik?
Tidak dapat diasumsikan sama. Justru inilah alasan studi scaling saat ini tidak boleh dianggap sebagai causal effect dari \(N\).
Jika total power disamakan dengan total power konfigurasi \(N=3\), yaitu 14.77 dBm, maka:
\(N=3\): 10 dBm per TX;
\(N=5\): sekitar 7.78 dBm per TX;
\(N=9\): sekitar 5.23 dBm per TX.
Dengan demikian, keuntungan 4.77 dB total power yang sekarang dimiliki \(N=9\) akan hilang. Link capacity \(N=9\) kemungkinan turun dibandingkan hasil sekarang.
Jika aperture juga dipertahankan 0.90 m, spacing menjadi:
\(N=3\): 0.45 m;
\(N=5\): 0.225 m;
\(N=9\): 0.1125 m.
Perubahan spacing tersebut akan mengubah phase progression, spatial correlation, dan singular-value spectrum.
Jawaban sidang:
Saya tidak mengharapkan hasil numeriknya tetap sama. Studi sekarang membandingkan complete configurations karena total power, aperture, dan angular sampling berubah bersama order. Untuk mengisolasi order, simulasi harus diulang dengan fixed total power, fixed aperture, common angular coverage, dan nested RX-angle grids. Hanya setelah itu perbedaan dapat diatribusikan terutama kepada penambahan dimensi MIMO.

Kesimpulan paling aman: studi sekarang membuktikan absolute capacity growth dengan diminishing per-dimension efficiency, tetapi belum membuktikan keuntungan causal dari peningkatan MIMO order.

Mengapa Chapter 2 menggunakan patch antenna, tetapi Chapter 3 menggunakan isotropic TX? Apakah hasilnya masih konsisten?
Arah jawaban: Isotropic TX dipilih untuk menghilangkan pengaruh TX radiation pattern sehingga perbandingan berfokus pada complete RX design. Namun, hasil Chapter 3 menjadi evaluasi idealized system dan tidak langsung mewakili implementasi patch-to-lens fisik.

Mengapa RX dipilih pada \(0^\circ,\pm45^\circ\), padahal kualitas fokus sudah memburuk pada sudut besar?
Arah jawaban: Sudut tersebut dipilih untuk memberikan separasi angular yang jelas. Namun, penggunaan \(\pm45^\circ\) juga memperkenalkan scan loss dan sidelobe yang dapat menurunkan aggregate capacity. Pemilihan posisi RX seharusnya dioptimalkan dari focal-field response, bukan ditetapkan apriori.

Karakterisasi focal field banyak menggunakan sudut negatif. Bagaimana Anda menjamin respons sudut positif simetris?
Arah jawaban: Simetri dapat diharapkan dari geometri lensa yang radial/fourfold symmetric, tetapi harus diverifikasi dengan full-wave simulation. Simetri geometri saja tidak menjamin respons identik apabila feed, mesh, polarization, atau lingkungan tidak simetris.

Bagaimana unit-cell state dipilih untuk setiap posisi? Apakah hanya berdasarkan phase terdekat?
Arah jawaban: Jika hanya nearest wrapped phase yang digunakan, amplitude transmission tidak ikut dioptimalkan. Metode yang lebih baik meminimalkan weighted complex error, misalnya
\[
\left|T_ne^{j\phi_n}-T_{\text{target}}e^{j\phi_{\text{target}}}\right|.
\]Tesis perlu menjelaskan mapping rule dan nilai RMS phase error final.

Mengapa menggunakan transmit radiation pattern sebagai receive pattern?
Arah jawaban: Hal tersebut didasarkan pada electromagnetic reciprocity untuk struktur pasif, linear, dan reciprocal. Validitasnya memerlukan polarization, impedance reference, coordinate system, dan phase center yang sama.

Apakah struktur lima lapis dengan air gap 1 mm realistis untuk difabrikasi pada 38 GHz?
Arah jawaban: Secara simulasi memungkinkan, tetapi alignment error, variasi air gap, ketebalan tembaga, dan toleransi feature size dapat menyebabkan phase error besar. Karena tidak ada tolerance study dan prototype, fabrication robustness belum terbukti.

Pemodelan kanal dan solver
Mengapa Chapter 2 memakai ruangan \(3\times5\times3\) m, sedangkan Chapter 3 memakai \(20\times20\times3\) m?
Arah jawaban: Ruangan kecil digunakan untuk cross-solver component-level validation, sedangkan ruangan besar digunakan untuk mobility study. Karena environment berbeda, angka kapasitas kedua bab tidak boleh dibandingkan langsung; hanya mekanisme dan kecenderungannya yang dapat dihubungkan.

Apakah tiga frequency points, 37, 38, dan 39 GHz, cukup untuk menyatakan cross-frequency robustness?
Arah jawaban: Tidak cukup untuk mengklaim broadband robustness. Ketiganya hanya anchor points. Evaluasi bandwidth yang kuat memerlukan frequency sweep lebih rapat, focal shift, gain, sidelobe, singular values, dan capacity versus frequency.

Berapa maximum reflection depth, diffraction order, scattering mechanism, dan material parameters yang digunakan pada ray tracing?
Arah jawaban: Jumlah path samples saja belum cukup mendefinisikan fidelity ray tracing. Jika parameter tersebut belum dicatat, akui sebagai reproducibility limitation karena perubahan material, maximum depth, diffraction, dan scattering dapat mengubah multipath structure.

HFSS SBR+ dan Hybrid memberi baseline correlation yang berbeda. Mana yang lebih benar?
Arah jawaban: Tidak ada ground truth eksperimental untuk menentukan salah satunya. Hybrid memasukkan full-wave near-field interaction melalui FEM, sedangkan SBR+ menggunakan approximation yang lebih sederhana. Perbedaan baseline menunjukkan solver uncertainty, sehingga klaim terkuat hanya qualitative trend.

Apakah penggunaan imported lens pattern di Sionna menghilangkan interaksi lensa dengan lingkungan?
Arah jawaban: Ya, lensa diperlakukan sebagai bagian dari effective composite antenna pattern, bukan sebagai objek scattering eksplisit dalam scene. Ini menangkap directional response, tetapi tidak menangkap kemungkinan near-field interaction atau scattering lingkungan dari physical lens structure.

Definisi metrik
Apakah “spatial correlation” dalam tesis benar-benar correlation statistik?
Arah jawaban: Tidak sepenuhnya. Persamaan yang digunakan adalah normalized complex inner product atau channel coherence karena tidak ada mean subtraction dan expectation atas ensemble:
\[
\rho_{ij}=
\frac{\mathbf h_i\mathbf h_j^H}
{\|\mathbf h_i\|\|\mathbf h_j\|}.
\]Istilah yang lebih presisi adalah normalized channel coherence.

Mengapa effective rank dihitung menggunakan \(\sigma_i^2\), bukan \(\sigma_i\)?
Arah jawaban: Kuadrat singular value merepresentasikan eigenmode power sehingga entropy dihitung dari distribusi daya. Namun, literatur juga mempunyai definisi berdasarkan singular value langsung. Definisi harus disebutkan secara eksplisit karena hasil numeriknya dapat berbeda.

Condition number mencapai 71.89 dB. Apakah itu physical result atau numerical noise?
Arah jawaban: Nilai tersebut menunjukkan \(\sigma_{\min}\) sangat kecil dibandingkan \(\sigma_{\max}\), tetapi bisa sensitif terhadap numerical precision dan ray-tracing truncation. Harus ditunjukkan singular-value spectrum, numerical floor, serta sensitivity terhadap jumlah rays sebelum menyatakan rank deficiency secara fisik.

Mengapa condition number dalam dB dihitung dengan \(20\log_{10}\kappa\), bukan \(10\log_{10}\kappa\)?
Arah jawaban: Karena \(\kappa\) adalah rasio singular-value amplitude. Jika yang dibandingkan adalah eigenmode power \(\sigma_1^2/\sigma_N^2\), hasilnya ekuivalen dengan \(10\log_{10}\) power ratio.

Mengapa kapasitas dirata-ratakan sebagai mean dari \(\log_2(1+\gamma(f))\), bukan log dari mean SNR?
Arah jawaban: Mean-log sesuai untuk parallel frequency channels dengan equal resource allocation. Karena fungsi log bersifat concave,
\[
\mathbb E[\log(1+\gamma)]
\neq
\log(1+\mathbb E[\gamma]).
\]Log dari mean SNR akan cenderung meng-overestimate kapasitas kanal frequency-selective.

Mengapa Chapter 2 memakai 20 dB, sedangkan Chapter 3 memakai 10 dB?
Arah jawaban: Keduanya berasal dari evaluation frameworks yang berbeda. Karena SNR dan normalisasinya berbeda, kapasitas antarbab tidak boleh dibandingkan langsung. Untuk konsistensi, sebaiknya ditambahkan sensitivity curve pada beberapa nilai SNR yang sama.

Interpretasi hasil
Bagaimana lensa pasif dapat memberikan “gain” tanpa melanggar konservasi energi?
Arah jawaban: Lensa tidak menghasilkan energi. Ia memusatkan atau mengarahkan energi ke branch tertentu dengan mengorbankan arah atau branch lain, ditambah insertion loss. Karena itu matched link dapat meningkat sementara banyak mismatched links menurun.

Jika channel menjadi diagonal-dominant, bukankah rank otomatis menjadi baik?
Arah jawaban: Tidak. Matriks diagonal hanya memiliki effective rank tinggi jika nilai diagonalnya relatif seimbang. Jika satu diagonal membawa sekitar 60% total power sedangkan lainnya lemah, matriks tetap dapat memiliki poor effective rank.

Apakah baseline tanpa lensa merupakan pembanding terbaik? Bagaimana jika dibandingkan dengan phased array atau hybrid beamforming?
Arah jawaban: Baseline sekarang adalah fixed conventional patch-array design, bukan optimized state-of-the-art receiver. Hasil tidak membuktikan lensa lebih baik atau lebih buruk daripada phased array yang melakukan beamforming. Perbandingan tersebut memerlukan kesamaan aperture, RF-chain count, total power, dan beam-training overhead.

Apa arti “21 validation checks passed”? Apakah itu membuktikan hasil simulasi benar secara fisik?
Arah jawaban: Tidak. Validation checks hanya menunjukkan konsistensi tabel, parsing, rekonsiliasi angka, dan file hasil. Itu bukan validasi electromagnetic model, statistical convergence, atau experimental correctness.

Mengapa median digunakan sebagai hasil utama, bukan mean atau lower-tail capacity?
Arah jawaban: Median lebih robust terhadap extreme aligned dan misaligned branches, tetapi menyembunyikan tail behavior. Karena sistem komunikasi sering ditentukan oleh worst-case reliability, median sebaiknya dilengkapi mean, CDF, persentil ke-5, dan persentil ke-95.

