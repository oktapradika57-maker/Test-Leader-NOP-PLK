import streamlit as st
import streamlit.components.v1 as components
import urllib.parse
import time
import random

# ==========================================
# KONFIGURASI UTAMA
# ==========================================
NOMOR_WA_KOORDINATOR = "628115251515"

st.set_page_config(page_title="Assessment 100 Soal Calon Leader", page_icon="📋", layout="centered")

# ==========================================
# FUNGSI PENGACAK OPSI DETERMINISTIK (ANTI POLA B SEMUA & ANTI CONTEK)
# ==========================================
def get_shuffled_options(nama_kandidat, q_item):
    """
    Mengacak posisi opsi A, B, C, D untuk setiap soal dan setiap kandidat.
    Menggunakan seed deterministik agar posisi opsi tidak berubah saat tombol diklik,
    namun letak jawaban 5 poin tersebar acak di A, B, C, dan D.
    """
    seed_str = f"{nama_kandidat.lower().strip()}_soal_{q_item['id']}_kut_plk"
    rng = random.Random(seed_str)
    opsi_list = list(q_item["opts"])  # List of tuples: (teks_jawaban, poin)
    rng.shuffle(opsi_list)
    huruf = ["A", "B", "C", "D"]
    return {huruf[i]: opsi_list[i] for i in range(len(opsi_list))}

# ==========================================
# KOMPONEN VISUAL COUNTDOWN TIMER
# ==========================================
def tampilkan_timer_visual(sisa_detik, nomor_bagian):
    timer_html = f"""
    <div style="background-color:#1e293b; color:#f8fafc; padding:12px 18px; border-radius:10px; 
                display:flex; justify-content:space-between; align-items:center; font-family:sans-serif; 
                border-left: 6px solid #3b82f6; margin-bottom:10px;">
        <div>
            <span style="font-size:14px; color:#94a3b8;">⏱️ Batas Waktu Bagian {nomor_bagian} (11 Bagian):</span><br>
            <strong style="font-size:15px;">Baca setiap opsi dengan teliti (Urutan opsi diacak sistem)</strong>
        </div>
        <div id="countdown_{nomor_bagian}" style="font-size:26px; font-weight:bold; color:#38bdf8; background:#0f172a; padding:6px 14px; border-radius:8px;">
            --:--
        </div>
    </div>
    <script>
        var timeleft = {int(sisa_detik)};
        var display = document.getElementById("countdown_{nomor_bagian}");
        function updateTimer() {{
            if (timeleft <= 0) {{
                display.innerHTML = "WAKTU HABIS!";
                display.style.color = "#ef4444";
            }} else {{
                var m = Math.floor(timeleft / 60);
                var s = timeleft % 60;
                display.innerHTML = (m < 10 ? "0"+m : m) + ":" + (s < 10 ? "0"+s : s);
                if (timeleft < 60) {{
                    display.style.color = "#facc15";
                }}
                timeleft -= 1;
            }}
        }}
        updateTimer();
        setInterval(updateTimer, 1000);
    </script>
    """
    components.html(timer_html, height=85)

# ==========================================
# ANALISIS LEVEL & KECENDERUNGAN SIFAT (MAX 500 POIN)
# ==========================================
def analisis_level_dan_sifat_100(total_skor, kat, penalti_waktu):
    sifat = []
    
    # 1. PENENTUAN LEVEL KANDIDAT (Skala 500 Poin)
    if total_skor >= 425 and kat[6] >= 20 and kat[10] >= 55 and kat[11] >= 40:
        level = "LEADER TANGGUH, STRATEGIS & BERINTEGRITAS (Sangat Layak)"
        sifat.append("✅ Matang secara kepemimpinan, tajam dalam hitungan teknis power, piawai berkomunikasi dengan mitra eksternal, serta memiliki pola pikir bisnis & efisiensi risiko yang kuat.")
    elif total_skor >= 355 and kat[6] >= 18:
        level = "KANDIDAT CALON LEADER POTENSIAL (Perlu Pendampingan Terarah)"
        sifat.append("⚠️ Memiliki fondasi dasar sebagai calon leader, namun masih memerlukan penguatan pada ketegasan manajerial, ketelitian hitungan daya, atau negosiasi lintas perusahaan.")
    else:
        level = "MENTALITAS TEKNISI PELAKSANA (Belum Layak Menjadi Leader)"
        sifat.append("❌ Pola pikir masih sebatas pelaksana teknis individu. Belum memiliki ketajaman analisis biaya/risiko bisnis, lemah dalam perhitungan teknis power, atau kurang tegas menegakkan aturan.")

    # 2. KECENDERUNGAN SIFAT PER DIMENSI
    if kat[1] >= 20:
        sifat.append("🔸 [Kepemimpinan]: Tegas mendelegasikan tugas & berani bertanggung jawab penuh atas SLA tim.")
    else:
        sifat.append("🔸 [Kepemimpinan]: Cenderung ragu mengatur anggota atau mengambil alih pekerjaan sendiri.")

    if kat[2] + kat[4] >= 40:
        sifat.append("🔸 [Teknis & Taktis]: Sistematis dalam triage prioritas gangguan & fokus pada Root Cause Analysis.")
    else:
        sifat.append("🔸 [Teknis & Taktis]: Mudah terdistraksi saat gangguan ganda & masih berpola tambal-sulam.")

    if kat[6] >= 22:
        sifat.append("🔸 [Integritas]: TANPA KOMPROMI terhadap manipulasi data/BBM dan tegas merekomendasikan pemecatan pembangkang.")
    else:
        sifat.append("🔸 [Integritas]: PERINGATAN! Rawan berkompromi terhadap pelanggaran/manipulasi anggota karena rasa sungkan.")

    if kat[7] >= 60:
        sifat.append("🔸 [Etika & Penilaian Tim]: Hormat & solutif kepada atasan, objektif berbasis data saat menilai KPI bawahan.")
    else:
        sifat.append("🔸 [Etika & Penilaian Tim]: Penilaian terhadap anggota masih rawan bias subjektif/emosional.")

    if kat[9] >= 60:
        sifat.append("🔸 [Kemitraan Eksternal]: Profesional menjaga wibawa perusahaan, taktis bernegosiasi & berkolaborasi dengan mitra/vendor.")
    else:
        sifat.append("🔸 [Kemitraan Eksternal]: Kurang taktis menghadapi pihak eksternal (mudah ditekan mitra atau justru memicu konflik).")

    if kat[10] >= 60:
        sifat.append("🔸 [Matematika Power]: Sangat akurat menghitung beban VA/Watt, kapasitas Ah baterai, backup time, dan konsumsi BBM.")
    elif kat[10] >= 45:
        sifat.append("🔸 [Matematika Power]: Cukup memahami logika dasar daya, namun kurang teliti pada hitungan efisiensi & pembebanan.")
    else:
        sifat.append("🔸 [Matematika Power]: LEMAH dalam perhitungan teknis power & estimasi matematis lapangan.")

    if kat[11] >= 42:
        sifat.append("🔸 [Pola Pikir Dana & Bisnis]: Memiliki kesadaran tinggi atas efisiensi biaya operasional, risiko denda SLA, dan kelancaran penagihan bisnis.")
    else:
        sifat.append("🔸 [Pola Pikir Dana & Bisnis]: Kurang peka terhadap pemborosan dana operasional dan dampak finansial bagi perusahaan.")

    if penalti_waktu == 0:
        sifat.append("🔸 [Manajemen Waktu]: Sangat disiplin, menyelesaikan seluruh 11 bagian tepat waktu.")
    else:
        sifat.append(f"🔸 [Manajemen Waktu]: Melewati batas waktu pada beberapa bagian (Penalti -{penalti_waktu} poin).")

    return level, "\n".join(sifat)

# ==========================================
# KONFIGURASI 11 BAGIAN & ALOKASI WAKTU
# ==========================================
SECTIONS = {
    1: {"title": "Bagian 1: Kepemimpinan & Manajemen Tim", "desc": "5 Soal | Fokus: Delegasi, Disiplin & Akuntabilitas", "minutes": 6},
    2: {"title": "Bagian 2: Teknis & Operasional Lapangan", "desc": "5 Soal | Fokus: Prioritas Triage, SOP & K3", "minutes": 8},
    3: {"title": "Bagian 3: Sudut Pandang & Ownership Kerja", "desc": "5 Soal | Fokus: Akuntabilitas Sistem & Kolaborasi Admin", "minutes": 6},
    4: {"title": "Bagian 4: Pola Pikir & Penyelesaian Masalah Taktis", "desc": "5 Soal | Fokus: Root Cause Analysis & Adaptabilitas", "minutes": 8},
    5: {"title": "Bagian 5: Kehidupan Pribadi vs Profesional", "desc": "10 Soal | Fokus: Batasan Emosi, Etika & Self-Leadership", "minutes": 10},
    6: {"title": "Bagian 6: Integritas, Norma Komunikasi & Ketegasan Pemecatan", "desc": "5 Soal | Fokus: Anti-Fraud & Tindak Tegas Pembangkang", "minutes": 6},
    7: {"title": "Bagian 7: Etika Berperilaku (Bos, Bawahan, Sesama) & Menilai Tim", "desc": "15 Soal | Fokus: Komunikasi Vertikal & Evaluasi KPI Individu", "minutes": 15},
    8: {"title": "Bagian 8: Penalaran Logis & Penyelesaian Masalah Kompleks", "desc": "10 Soal | Fokus: Logika Operasional & Keputusan Kritis", "minutes": 12},
    9: {"title": "Bagian 9: Kemitraan Eksternal & Komunikasi Lintas Perusahaan", "desc": "15 Soal | Fokus: Relasi Maincon, Vendor, Tower Provider & Negosiasi", "minutes": 15},
    10: {"title": "Bagian 10: Matematika Power, Analogi Daya & Hitungan Teknis", "desc": "15 Soal | Fokus: Kalkulasi Watt/Ampere, Ah Baterai, Genset & Fasa", "minutes": 20},
    11: {"title": "Bagian 11: Pola Pikir Dana, Manajemen Risiko & Bisnis Perusahaan", "desc": "10 Soal | Fokus: Efisiensi Opex, Risiko Penalti SLA & Profitabilitas", "minutes": 12}
}

# ==========================================
# DATABASE 100 SOAL (OPSI AKAN DIACAK OTOMATIS OLEH SISTEM)
# Format opts: List of (Teks Jawaban, Poin)
# ==========================================
QUESTIONS = [
    # ---------------- BAGIAN 1: KEPEMIMPINAN (1-5) ----------------
    {"id": 1, "sec": 1, "q": "1. Di tim Anda terdapat Anggota A yang sangat cepat menangani teknis lapangan namun sering lalai melengkapi dokumentasi, serta Anggota B yang sangat tertib administrasi namun lambat saat eksekusi teknis. Saat terjadi tiket gangguan mendesak, langkah pengaturan apa yang Anda ambil?",
     "opts": [
         ("Memasangkan keduanya secara terstruktur: Anggota A memimpin eksekusi teknis, sedangkan Anggota B mengawal kelengkapan data/foto secara real-time sambil mempelajari kecepatan kerja.", 5),
         ("Mengambil alih pekerjaan teknis terberat sendirian di lapangan agar kedua anggota tersebut cukup membantu hal-hal ringan tanpa berisiko salah.", 3),
         ("Menugaskan Anggota A berangkat sendiri agar gangguan cepat selesai, lalu meminta Anggota B menyusun laporan dari kantor berdasarkan cerita Anggota A.", 2),
         ("Memberikan teguran keras kepada keduanya sebelum berangkat agar tidak mengulangi kelemahan masing-masing selama bekerja di lokasi.", 1)
     ]},
    {"id": 2, "sec": 1, "q": "2. Seorang teknisi senior yang sangat diandalkan secara teknis berulang kali menunda pengisian laporan penutupan pekerjaan dengan alasan lelah dan merasa urusan administrasi bukan prioritas selama site sudah normal. Bagaimana sikap Anda?",
     "opts": [
         ("Memanggil secara empat mata, mengapresiasi keahlian teknisnya, namun menegaskan bahwa pekerjaan bernilai 0% jika laporan belum tuntas serta menerapkan konsekuensi disiplin yang konsisten.", 5),
         ("Melaporkannya langsung kepada Koordinator agar segera diterbitkan Surat Peringatan tanpa melalui diskusi internal terlebih dahulu.", 3),
         ("Membantu mengisikan sebagian laporannya secara pribadi agar target tim tidak terkunci sembari mengingatkannya secara lisan.", 2),
         ("Menegurnya secara terbuka di grup WhatsApp operasional agar menjadi pelajaran bagi teknisi senior maupun junior lainnya.", 1)
     ]},
    {"id": 3, "sec": 1, "q": "3. Target pencapaian SLA tim Anda bulan ini meleset akibat salah satu teknisi salah mengidentifikasi komponen rusak sehingga waktu perbaikan membengkak. Saat dievaluasi oleh Koordinator, bagaimana Anda menyampaikannya?",
     "opts": [
         ("Mengambil tanggung jawab penuh sebagai Leader atas kegagalan SLA tim, memaparkan akar kesalahan teknis secara objektif, dan menyerahkan rencana standarisasi pengecekan agar tidak terulang.", 5),
         ("Meminta teknisi yang bersangkutan hadir langsung menjelaskan kronologi kesalahannya kepada Koordinator agar informasinya tidak bias.", 3),
         ("Menjelaskan bahwa kegagalan tersebut dipicu oleh kondisi cuaca buruk dan keterbatasan waktu tempuh menuju lokasi yang sulit.", 2),
         ("Menyebutkan nama anggota yang melakukan kesalahan diagnosa sejak awal agar penilaian kinerja pribadi Anda sebagai Leader tetap aman.", 1)
     ]},
    {"id": 4, "sec": 1, "q": "4. Tim harus berangkat menangani gangguan kritis pada pukul 23.00 malam di tengah hujan deras, sementara anggota tim mulai menunjukkan penurunan moral dan mengeluhkan kelelahan fisik. Apa tindakan Anda?",
     "opts": [
         ("Hadir memastikan kesiapan sarana keselamatan dan logistik, memberikan arahan tenang mengenai dampak kritikalitas site, serta mengatur pembagian tugas dan giliran kemudi agar tetap aman.", 5),
         ("Memerintahkan tim tetap berangkat sesuai jadwal sambil memantau pergerakan mereka melalui telepon setiap satu jam dari rumah.", 3),
         ("Mengambil keputusan sepihak menunda keberangkatan hingga pukul 06.00 pagi demi menjaga kondisi fisik anggota tim.", 2),
         ("Menegaskan bahwa keluhan malam hari akan dicatat sebagai pengurang nilai evaluasi bulanan masing-masing anggota.", 1)
     ]},
    {"id": 5, "sec": 1, "q": "5. Anda menerima anggota baru yang belum menguasai prosedur pengukuran sistem power dan rectifier, padahal jadwal kunjungan preventif dan penanganan gangguan minggu ini sangat padat. Bagaimana strategi Anda?",
     "opts": [
         ("Membekalinya dengan daftar periksa (checklist) SOP standar, menugaskannya mendampingi teknisi senior di lapangan, dan melakukan evaluasi singkat 15 menit setiap sore.", 5),
         ("Mengajukan permohonan kepada Koordinator agar anggota baru tersebut ditukar dengan personel dari area lain yang sudah siap pakai.", 3),
         ("Memintanya mengamati cara kerja rekan-rekannya secara mandiri di lapangan sampai ia memahami alur kerjanya sendiri.", 2),
         ("Menugaskannya khusus untuk pekerjaan pembersihan area site dan pengangkutan peralatan agar tidak menghambat durasi kerja teknis.", 1)
     ]},

    # ---------------- BAGIAN 2: TEKNIS OPERASIONAL (6-10) ----------------
    {"id": 6, "sec": 2, "q": "6. Masuk 3 tiket di waktu bersamaan: (1) Site A listrik PLN padam namun baterai cadangan sehat di level 92%, (2) Site B tegangan DC drop ke 45,2V dan genset gagal start otomatis, (3) Site C jadwal Preventive Maintenance rutin. Bagaimana urutan eksekusi yang tepat?",
     "opts": [
         ("Site B -> Site A -> Site C (mengamankan Site B yang kritis berisiko down, memantau/menyiapkan mobilisasi backup ke Site A, lalu menjadwalkan ulang PM Site C).", 5),
         ("Site A -> Site B -> Site C (mengikuti urutan kronologis masuknya tiket di sistem monitoring agar antrean tertib).", 3),
         ("Meminta petunjuk Koordinator terlebih dahulu sebelum menggerakkan tim ke salah satu dari ketiga lokasi tersebut.", 2),
         ("Site C -> Site A -> Site B (menyelesaikan pekerjaan PM rutin yang paling cepat tuntas terlebih dahulu).", 1)
     ]},
    {"id": 7, "sec": 2, "q": "7. Saat tiba di lokasi yang mengalami padam PLN, ditemukan unit genset tidak menyala otomatis dan pada layar modul kontrol DSE/SmartGen muncul alarm 'Failed to Start'. Langkah diagnosa teknis pertama yang paling sistematis adalah:",
     "opts": [
         ("Memeriksa parameter dasar secara berurutan: tegangan baterai stater, ketersediaan solar & kerja fuel solenoid, posisi tombol Emergency Stop, lalu menguji crank manual untuk memisahkan masalah elektrikal atau mekanikal.", 5),
         ("Melaporkan kepada Koordinator bahwa unit genset mengalami kerusakan mesin dan segera meminta pengiriman unit genset mobile cadangan.", 3),
         ("Membuka rangkaian panel kontrol AMF/ATS dan mengganti relay stater serta timer delay dengan komponen cadangan.", 2),
         ("Melakukan reset modul kontrol dan menekan tombol start berulang kali hingga mesin berhasil berputar.", 1)
     ]},
    {"id": 8, "sec": 2, "q": "8. Anda memeriksa laporan Preventive Maintenance yang baru dikirim anggota tim dan mendapati foto pengukuran tang ampere serta nilai tegangan sel baterai sangat identik dengan dokumentasi bulan lalu. Apa tindakan Anda?",
     "opts": [
         ("Menahan persetujuan laporan, memverifikasi metadata waktu foto, dan mewajibkan tim melakukan pengukuran ulang secara langsung melalui panggilan video atau kunjungan ulang.", 5),
         ("Menghapus laporan tersebut dari rekapitulasi harian dan meminta anggota tim membuat laporan baru keesokan harinya.", 3),
         ("Menyesuaikan beberapa angka desimal pada tabel laporan agar tidak terlihat sama persis dengan laporan periode sebelumnya.", 2),
         ("Tetap meneruskan laporan tersebut ke admin agar target persentase penyelesaian PM mingguan tidak terlihat menurun.", 1)
     ]},
    {"id": 9, "sec": 2, "q": "9. Sebelum tim melakukan perjalanan sejauh 3 jam menuju site pedalaman untuk perbaikan gangguan power, prosedur kesiapan apa yang wajib Anda verifikasi sebagai Leader?",
     "opts": [
         ("Memverifikasi fungsi alat ukur (multimeter, tang ampere), kelengkapan toolkit, ketersediaan suku cadang cadangan sesuai indikasi alarm, kesiapan APD K3, serta kondisi kendaraan.", 5),
         ("Memastikan bahan bakar kendaraan operasional sudah terisi penuh dan tim sudah membawa tas peralatan standar masing-masing.", 3),
         ("Menginstruksikan tim segera berangkat detik itu juga agar waktu respons (response time) tercatat cepat di sistem.", 2),
         ("Mempercayakan pengecekan kelengkapan alat sepenuhnya kepada teknisi yang bertugas tanpa perlu diperiksa ulang.", 1)
     ]},
    {"id": 10, "sec": 2, "q": "10. Dalam perbaikan panel AC bertegangan 380V yang menyisakan waktu 15 menit sebelum batas SLA terlampaui, teknisi meminta izin menyambung kabel dalam kondisi bertegangan tanpa APD lengkap agar cepat selesai. Keputusan Anda?",
     "opts": [
         ("Menolak tegas, mewajibkan pemutusan sumber tegangan dan penggunaan APD sesuai prosedur K3, sembari menginformasikan kondisi aktual kepada Koordinator.", 5),
         ("Menginstruksikan penghentian seluruh pekerjaan hari itu dan menarik tim kembali ke kantor demi menghindari risiko kecelakaan.", 3),
         ("Memberikan izin khusus satu kali ini dengan pengawasan ketat agar target SLA tim tidak tercatat merah.", 2),
         ("Membiarkan teknisi melakukannya selama tidak terekam di dalam dokumentasi foto yang dikirim ke grup.", 1)
     ]},

    # ---------------- BAGIAN 3: SUDUT PANDANG (11-15) ----------------
    {"id": 11, "sec": 3, "q": "11. Manajemen memberlakukan sistem penguncian otomatis: teknisi tidak dapat mengajukan dana operasional baru apabila laporan pekerjaan sebelumnya belum diunggah lengkap. Anggota tim mengeluhkan aturan ini. Bagaimana sudut pandang Anda?",
     "opts": [
         ("Mendukung penuh sistem tersebut sebagai kontrol akuntabilitas, lalu mendisiplinkan anggota untuk langsung mengunggah laporan sesaat setelah pekerjaan tuntas di lokasi.", 5),
         ("Meminta anggota tim menyampaikan keberatan mereka secara langsung kepada Admin Operasional saat pengajuan dana.", 3),
         ("Mengizinkan pengisian data sementara seadanya di sistem agar kunci pengajuan dana terbuka saat kondisi mendesak.", 2),
         ("Menilai kebijakan tersebut kurang realistis dengan beban kerja lapangan dan ikut mengeluhkannya bersama tim.", 1)
     ]},
    {"id": 12, "sec": 3, "q": "12. Saat mengunjungi site hanya untuk mengganti lampu indikator panel, Anda melihat ada terminasi kabel beban utama pada DCPDB yang berubah warna karena panas berlebih, meski belum menimbulkan alarm. Sikap Anda?",
     "opts": [
         ("Melakukan pengencangan dan penanganan pencegahan yang aman saat itu juga, mendokumentasikan sebelum-sesudah, serta melaporkannya sebagai temuan preventif.", 5),
         ("Mengambil foto kondisi kabel tersebut sebagai catatan pribadi untuk dijadwalkan pada kunjungan pemeliharaan bulan depan.", 3),
         ("Tetap fokus menyelesaikan tiket lampu indikator saja agar jadwal kunjungan ke lokasi berikutnya tidak mundur.", 2),
         ("Membiarkan kondisi tersebut hingga muncul tiket gangguan resmi agar dihitung sebagai tambahan produktivitas tim.", 1)
     ]},
    {"id": 13, "sec": 3, "q": "13. Dalam rapat evaluasi, Koordinator menyoroti bahwa data audit power dari tim Anda memiliki tingkat kesalahan input tertinggi dibanding area lain. Bagaimana respons Anda?",
     "opts": [
         ("Menerima evaluasi secara terbuka, memetakan letak kesalahan input anggota, dan menerapkan pemeriksaan silang (verifikasi Leader) sebelum data diserahkan.", 5),
         ("Menegur keras seluruh anggota tim dan admin penginput segera setelah rapat selesai karena membuat malu area.", 3),
         ("Merasa kurang diapresiasi karena tim Anda sebenarnya sudah bekerja paling berat secara fisik di medan yang sulit.", 2),
         ("Menyampaikan argumen bahwa kesalahan penulisan angka tidak berdampak fatal selama perangkat di site tetap beroperasi normal.", 1)
     ]},
    {"id": 14, "sec": 3, "q": "14. Seusai perbaikan darurat, terdapat sisa material kabel dan sisa dana pembelian suku cadang sebesar Rp 150.000. Anggota tim menyarankan agar sisa tersebut digunakan untuk makan bersama tanpa perlu dilaporkan. Sikap Anda?",
     "opts": [
         ("Menolak dengan tegas namun edukatif, menjelaskan bahwa integritas adalah prinsip mutlak, dan mengembalikan seluruh sisa dana/material beserta bukti nota asli.", 5),
         ("Menyerahkan keputusan sepenuhnya kepada anggota yang memegang uang tersebut tanpa ingin ikut campur.", 2),
         ("Menyetujui usulan tersebut sebagai bentuk apresiasi lelah tim selama nominalnya masih di bawah Rp 200.000.", 1),
         ("Menyimpan sisa dana tersebut sebagai kas tidak tercatat di tangan Anda untuk cadangan taktis di kemudian hari.", 2)
     ]},
    {"id": 15, "sec": 3, "q": "15. Admin Operasional menginformasikan bahwa ada 4 tiket pekerjaan tim Anda minggu lalu yang berstatus 'Belum Selesai' di rekapitulasi kantor, padahal tim merasa sudah mengerjakannya. Bagaimana Anda menyelesaikannya?",
     "opts": [
         ("Menjadikan Admin sebagai mitra kerja; segera menyandingkan bukti log lapangan, foto timestamp, dan nomor tiket secara tertib untuk menemukan titik selisihnya.", 5),
         ("Meminta Koordinator menengahi dan memeriksa cara kerja Admin dalam merekap laporan harian dari grup.", 3),
         ("Mengabaikan catatan Admin karena yakin bahwa perangkat di keempat lokasi tersebut sudah beroperasi normal.", 2),
         ("Menyalahkan Admin di grup komunikasi karena dianggap tidak teliti memantau pesan laporan dari tim lapangan.", 1)
     ]},

    # ---------------- BAGIAN 4: PROBLEM SOLVING (16-20) ----------------
    {"id": 16, "sec": 4, "q": "16. Sebuah site mengalami gangguan trip MCB input rectifier sebanyak 3 kali dalam 2 minggu terakhir. Teknisi selalu menyelesaikannya hanya dengan menaikkan kembali tuas MCB. Bagaimana pola pikir penyelesaian masalah Anda?",
     "opts": [
         ("Menghentikan penanganan sementara; melakukan Root Cause Analysis dengan mengukur lonjakan arus inrush, kapasitas MCB, kualitas koneksi, dan profil beban puncak untuk perbaikan permanen.", 5),
         ("Mengusulkan penggantian seluruh unit kabinet rectifier karena usia perangkat di lokasi tersebut sudah cukup tua.", 3),
         ("Tetap menginstruksikan penaikan MCB secara cepat setiap kali trip agar durasi downtime tiket selalu tercatat singkat.", 2),
         ("Meminta rotasi wilayah agar pengelolaan site yang bermasalah tersebut dialihkan ke tim teknisi yang lain.", 1)
     ]},
    {"id": 17, "sec": 4, "q": "17. Saat tim sedang menuju lokasi gangguan kritis (jarak 1 jam lagi), mobil operasional mengalami pecah ban dan di saat bersamaan diketahui satu konektor cadangan yang dibawa ternyata salah ukuran. Langkah taktis Anda?",
     "opts": [
         ("Membagi peran secara paralel: satu anggota menangani penggantian ban/transportasi alternatif, sementara Anda berkoordinasi mencari konektor pengganti di toko/rekan terdekat sekaligus memperbarui estimasi waktu ke Koordinator.", 5),
         ("Tetap melanjutkan perjalanan secara perlahan dengan kondisi ban bermasalah demi memastikan tim tiba di lokasi sesuai target awal.", 3),
         ("Memutuskan kembali ke kantor untuk mengambil konektor yang benar sekaligus memperbaiki ban di bengkel langganan.", 2),
         ("Menunggu perbaikan ban selesai sepenuhnya terlebih dahulu sebelum memikirkan solusi kekurangan konektor.", 1)
     ]},
    {"id": 18, "sec": 4, "q": "18. Anda diberikan tabel histori pengukuran tegangan akhir baterai (end voltage), suhu shelter, dan durasi backup selama 3 bulan terakhir dari 40 site. Bagaimana Anda mengolah data tersebut?",
     "opts": [
         ("Mengelompokkan site dengan tren penurunan performa paling curam untuk dijadikan prioritas jadwal perbaikan preventif sebelum jatuh menjadi gangguan.", 5),
         ("Menyimpan file tersebut dengan rapi sebagai dokumen pendukung apabila sewaktu-waktu diperiksa oleh tim audit.", 3),
         ("Menyerahkan kembali data tersebut kepada Koordinator untuk ditentukan lokasi mana saja yang harus dikunjungi.", 2),
         ("Memilih site-site yang datanya paling stabil dan normal untuk dimasukkan ke dalam laporan pencapaian bulanan.", 1)
     ]},
    {"id": 19, "sec": 4, "q": "19. Di tengah penanganan gangguan kritis, dua teknisi Anda berselisih paham cukup keras mengenai sumber kerusakan—satu menunjuk modul kontrol, satu lagi menunjuk sensor—sehingga pekerjaan terhenti. Tindakan Anda?",
     "opts": [
         ("Menengahi dengan tenang, menghentikan perdebatan asumsi, dan memimpin pengujian terukur menggunakan multimeter pada masing-masing titik untuk membuktikan sumber kerusakan secara faktual.", 5),
         ("Mengambil alih peralatan dari tangan keduanya dan menyelesaikan sendiri sisa pekerjaan perbaikan hingga tuntas.", 3),
         ("Membiarkan keduanya berargumen sejenak sampai salah satu pihak berhasil meyakinkan pihak lainnya.", 2),
         ("Mengikuti pendapat teknisi yang masa kerjanya lebih lama tanpa perlu melakukan pengukuran ulang.", 1)
     ]},
    {"id": 20, "sec": 4, "q": "20. Pada hari Rabu pagi, rencana kerja mingguan yang sudah berjalan rapi harus berubah karena ada instruksi mendadak untuk melakukan audit power di 6 site prioritas sebelum Jumat sore. Bagaimana Anda beradaptasi?",
     "opts": [
         ("Melakukan re-planning cepat: memetakan ulang dan menggabungkan rute site audit yang searah dengan jadwal PM rutin, membagi beban tim, dan melaporkan penyesuaian jadwal ke Koordinator.", 5),
         ("Melaksanakan instruksi audit secara acak tanpa memperbarui jadwal tertulis karena perubahan mendadak sering terjadi.", 3),
         ("Membatalkan seluruh jadwal PM rutin minggu ini secara total agar tim hanya mengerjakan 6 site audit tersebut.", 2),
         ("Menyampaikan keberatan karena perubahan mendadak merusak kerapian jadwal mingguan yang sudah disusun.", 1)
     ]},

    # ---------------- BAGIAN 5: KEHIDUPAN PRIBADI VS PROFESIONAL (21-30) ----------------
    {"id": 21, "sec": 5, "q": "21. Seorang anggota tim kerap menelepon Anda di atas pukul 23.00 malam untuk membicarakan keluhan pribadi dan urusan administrasi ringan yang tidak mendesak. Bagaimana Anda menetapkan batasan?",
     "opts": [
         ("Menetapkan aturan komunikasi yang tegas namun sopan: selalu siaga 24 jam untuk eskalasi gangguan darurat, namun mengarahkan bahasan non-darurat pada jam kerja esok hari.", 5),
         ("Tetap melayani seluruh pembicaraan tersebut setiap malam agar anggota tidak merasa dijauhi oleh pimpinannya.", 2),
         ("Mematikan nada dering telepon sepenuhnya setiap malam mulai pukul 21.00 hingga pagi hari berikutnya.", 1),
         ("Menegur dengan nada tinggi dan memblokir sementara nomor anggota tersebut agar waktu istirahat tidak terganggu.", 1)
     ]},
    {"id": 22, "sec": 5, "q": "22. Kinerja seorang teknisi andalan Anda menurun tajam dalam 2 minggu terakhir karena ia sedang mengalami persoalan keluarga yang cukup berat di rumah. Bagaimana sikap profesional Anda?",
     "opts": [
         ("Mengajak bicara empat mata secara empatik, mengatur penyesuaian beban/rute sementara agar ia dapat menata kondisinya, sambil tetap menyepakati batas standar kerja minimal.", 5),
         ("Memberikan potongan nilai kinerja secara langsung setiap kali ia melakukan kesalahan tanpa menanyakan urusan pribadinya.", 2),
         ("Menceritakan permasalahan keluarga teknisi tersebut kepada anggota tim lain agar mereka ikut memaklumi.", 1),
         ("Mengajukan penggantian personel secara langsung karena urusan rumah tangga tidak boleh terbawa ke kantor.", 1)
     ]},
    {"id": 23, "sec": 5, "q": "23. Saat Anda sedang menikmati waktu libur akhir pekan bersama keluarga, muncul laporan gangguan minor yang sebenarnya sesuai SOP dapat ditangani sepenuhnya oleh teknisi piket. Apa yang Anda lakukan?",
     "opts": [
         ("Mendelegasikan eksekusi sepenuhnya kepada teknisi piket, memantau progresnya secara berkala melalui sistem/grup, dan tetap siaga apabila diperlukan eskalasi.", 5),
         ("Meninggalkan agenda keluarga saat itu juga dan langsung berangkat mengerjakan sendiri gangguan minor tersebut.", 2),
         ("Menegur teknisi piket karena mengabarkan gangguan minor pada saat Anda sedang menjalani jadwal libur.", 1),
         ("Mengabaikan pesan di grup kerja sampai hari Senin pagi tiba karena sedang berada di luar jam kerja.", 1)
     ]},
    {"id": 24, "sec": 5, "q": "24. Salah satu anggota di dalam tim Anda merupakan sahabat dekat atau kerabat yang sudah sangat akrab di luar pekerjaan. Bagaimana Anda menempatkan posisi saat mengevaluasi kinerjanya?",
     "opts": [
         ("Menerapkan standar disiplin, target SLA, teguran, dan penilaian yang 100% setara dan objektif tanpa perlakuan khusus.", 5),
         ("Memberikan beban kerja yang justru jauh lebih berat dibanding anggota lain agar Anda tidak dituduh pilih kasih.", 3),
         ("Menempatkannya pada tugas-tugas ringan di dalam kota untuk menghindari potensi gesekan yang merusak hubungan pertemanan.", 2),
         ("Memberikan kelonggaran waktu pelaporan karena sudah memahami karakter pribadinya sehari-hari.", 1)
     ]},
    {"id": 25, "sec": 5, "q": "25. Anda baru saja mendapat tekanan keras dari manajemen terkait pencapaian area, dan beberapa menit kemudian seorang anggota tim melakukan kesalahan input laporan yang sepele. Bagaimana Anda mengelola respons?",
     "opts": [
         ("Mengendalikan emosi pribadi, mengoreksi kesalahan input anggota secara terfokus dan tenang, lalu menyusun langkah perbaikan target untuk manajemen.", 5),
         ("Memilih diam dan tidak menegur kesalahan anggota tersebut karena khawatir tidak mampu menahan kemarahan.", 2),
         ("Meluapkan kekesalan akibat tekanan manajemen tersebut dengan memarahi anggota yang salah input di depan tim.", 1),
         ("Menyatakan keinginan mengundurkan diri dari posisi Leader di hadapan tim karena tingginya tekanan kerja.", 1)
     ]},
    {"id": 26, "sec": 5, "q": "26. Anda melihat seorang anggota tim mengunggah keluhan bernada sindiran terhadap kebijakan operasional perusahaan di status media sosial pribadinya. Apa langkah Anda?",
     "opts": [
         ("Menegur secara pribadi, memberikan pemahaman mengenai etika profesional dan kerahasiaan internal perusahaan, serta meminta unggahan tersebut segera dihapus.", 5),
         ("Membiarkan unggahan tersebut karena menganggap akun media sosial merupakan ranah privasi masing-masing individu.", 2),
         ("Memberikan komentar teguran secara terbuka langsung pada kolom status media sosial anggota tersebut.", 1),
         ("Ikut menyukai unggahan tersebut sebagai bentuk solidaritas terhadap keluhan kerja di lapangan.", 1)
     ]},
    {"id": 27, "sec": 5, "q": "27. Ketika Anda sedang menghadiri acara keluarga yang penting, terjadi gangguan *site down* berskala besar yang membutuhkan komando koordinasi seorang Leader. Bagaimana keputusan Anda?",
     "opts": [
         ("Meminta izin sejenak secara bijak kepada keluarga untuk memimpin koordinasi taktis dan pemantauan pemulihan darurat hingga terkendali, lalu kembali melanjutkan waktu keluarga.", 5),
         ("Menyerahkan penanganan sepenuhnya kepada anggota di lapangan sambil sesekali melihat grup tanpa memberikan arahan.", 2),
         ("Menonaktifkan komunikasi kantor selama acara berlangsung agar tidak mengganggu suasana keluarga.", 1),
         ("Menyalahkan anggota tim secara emosional karena tidak mampu mencegah terjadinya gangguan di saat Anda sedang ada acara.", 1)
     ]},
    {"id": 28, "sec": 5, "q": "28. Di dalam tim Anda mulai terlihat gejala pengelompokan (kubu senior vs kubu junior) yang membuat koordinasi serah-terima pekerjaan menjadi dingin dan saling menyalahkan. Tindakan Anda?",
     "opts": [
         ("Mengumpulkan seluruh tim, menegaskan kesatuan tujuan operasional, merombak pasangan kerja secara silang (senior-junior), dan menindak tegas sikap tidak kooperatif.", 5),
         ("Membiarkan dinamika tersebut berjalan alami dengan harapan persaingan antarkelompok dapat memacu kecepatan kerja.", 2),
         ("Lebih banyak berkoordinasi melalui kelompok senior saja karena mereka lebih cepat memahami instruksi teknis.", 1),
         ("Ikut membicarakan kelemahan salah satu kelompok saat sedang berkumpul dengan kelompok lainnya.", 1)
     ]},
    {"id": 29, "sec": 5, "q": "29. Muncul isu tidak resmi di kalangan teknisi bahwa akan ada pemotongan insentif operasional bulan depan, sehingga semangat kerja tim menurun. Apa langkah Anda sebagai Leader?",
     "opts": [
         ("Meredam spekulasi di tim, segera mengonfirmasi kebenaran informasi kepada Koordinator/Manajemen, dan menyampaikan penjelasan resmi secara transparan kepada anggota.", 5),
         ("Melarang keras seluruh anggota membicarakan isu tersebut dengan ancaman sanksi tanpa memberikan penjelasan fakta.", 2),
         ("Menunggu sampai anggota tim benar-benar mogok bekerja baru melaporkan situasi tersebut ke manajemen.", 1),
         ("Ikut menyebarkan kabar yang belum pasti tersebut ke rekan-rekan leader di area kerja lainnya.", 1)
     ]},
    {"id": 30, "sec": 5, "q": "30. Bagaimana cara Anda menerapkan evaluasi diri (*self-leadership*) setiap akhir bulan sebelum menuntut peningkatan kinerja dari anggota tim Anda?",
     "opts": [
         ("Mengkaji ulang data pencapaian tim secara objektif, mengidentifikasi kelemahan arahan/pengawasan pribadi bulan ini, dan meminta umpan balik dari Koordinator maupun Admin.", 5),
         ("Menyimpulkan bahwa seluruh keterlambatan target bulan ini murni disebabkan oleh kurangnya daya juang anggota di lapangan.", 2),
         ("Merasa pola kepemimpinan sudah sempurna selama tidak ada surat teguran resmi yang turun dari atasan.", 1),
         ("Menunggu adanya apresiasi atau pujian terlebih dahulu sebelum berinisiatif meningkatkan standar kerja bulan berikutnya.", 1)
     ]},

    # ---------------- BAGIAN 6: INTEGRITAS & KETEGASAN PEMECATAN (31-35) ----------------
    {"id": 31, "sec": 6, "q": "31. Anda menemukan bukti valid bahwa seorang teknisi berkeahlian tinggi sengaja memalsukan foto odometer dan melakukan mark-up nota BBM untuk keuntungan pribadi. Apa tindakan tegas Anda?",
     "opts": [
         ("Menindak tanpa kompromi sesuai aturan perusahaan: menyusun berita acara bukti pelanggaran dan mengajukan sanksi tegas/rekomendasi pemecatan karena kejujuran di atas keahlian teknis.", 5),
         ("Memberikan teguran lisan secara tertutup dan memintanya berjanji tidak mengulangi lagi tanpa melaporkannya ke manajemen.", 2),
         ("Memaklumi tindakan tersebut karena keahlian teknisnya masih sangat diandalkan untuk menangani site-site sulit.", 1),
         ("Meminta teknisi tersebut membagi selisih dana tersebut untuk kas konsumsi tim agar kasusnya tidak diperpanjang.", 0)
     ]},
    {"id": 32, "sec": 6, "q": "32. Seorang anggota tim secara terang-terangan menolak penugasan resmi dari Anda, menantang wewenang Anda di grup kerja, dan memprovokasi rekan lain untuk mengabaikan SOP. Langkah Anda?",
     "opts": [
         ("Memanggil dan menegur secara tegas, mendokumentasikan bukti pembangkangan secara tertulis, melaporkannya ke Koordinator, dan merekomendasikan pemutusan kerja jika menolak dibina demi menjaga wibawa organisasi.", 5),
         ("Mengalihkan tugas tersebut kepada anggota lain yang lebih patuh agar pekerjaan lapangan tetap selesai tanpa ribut.", 2),
         ("Membalas dengan makian keras dan tantangan fisik di depan anggota lainnya untuk menunjukkan kekuasaan.", 1),
         ("Memilih diam dan mengalah karena khawatir anggota tersebut melakukan sabotase di lapangan.", 1)
     ]},
    {"id": 33, "sec": 6, "q": "33. Dalam grup WhatsApp operasional resmi, seorang anggota menggunakan kata-kata kasar yang merendahkan rekan kerja dan admin. Bagaimana Anda menegakkan norma komunikasi?",
     "opts": [
         ("Menegur langsung secara tegas di grup bahwa etika dan norma komunikasi profesional wajib dipatuhi, lalu memanggil yang bersangkutan untuk pembinaan tertulis/SP.", 5),
         ("Menghapus anggota tersebut dari grup operasional tanpa memberikan penjelasan atau surat peringatan resmi.", 2),
         ("Membiarkan hal tersebut karena menganggap gaya bahasa kasar sudah biasa terjadi di kalangan pekerja lapangan.", 1),
         ("Ikut menanggapi dengan candaan agar suasana grup tidak terlihat terlalu kaku.", 1)
     ]},
    {"id": 34, "sec": 6, "q": "34. Saat melakukan audit di lapangan, pihak subkon/vendor menawarkan uang tunai kepada tim Anda agar temuan instalasi yang tidak sesuai standar tidak dicatat dalam laporan. Sikap Anda?",
     "opts": [
         ("Menolak dengan tegas, mengingatkan tim bahwa menerima suap adalah pelanggaran integritas berat yang berujung pemecatan, dan tetap mencatat seluruh temuan secara apa adanya.", 5),
         ("Menegur pihak vendor dengan kata-kata kasar di lokasi namun tidak melaporkan insiden tersebut ke manajemen.", 2),
         ("Membiarkan anggota tim menerima uang tersebut asalkan nama Anda tidak ikut disebut dalam berita acara.", 1),
         ("Menerima pemberian tersebut dan tetap mencatat sebagian kecil temuan saja sebagai kompromi.", 0)
     ]},
    {"id": 35, "sec": 6, "q": "35. Seorang teknisi telah menerima 3 kali peringatan tertulis akibat akumulasi pelanggaran: manipulasi laporan, pembangkangan instruksi, dan sikap toksik yang merusak moral tim. Keputusan akhir Anda sebagai Leader?",
     "opts": [
         ("Mengajukan rekomendasi pemecatan secara resmi kepada manajemen lengkap dengan rekam jejak pelanggarannya, demi melindungi budaya kerja dan anggota tim lain yang berintegritas.", 5),
         ("Membiarkannya tetap terdaftar di tim namun tidak pernah lagi memberinya jadwal penugasan lapangan.", 2),
         ("Memberikan kesempatan keempat dan kelima karena alasan kemanusiaan dan rasa tidak tega terhadap keluarganya.", 1),
         ("Memotong uang operasional hariannya secara sepihak di luar ketentuan perusahaan sebagai hukuman.", 1)
     ]},

    # ---------------- BAGIAN 7: ETIKA BOS-BAWAHAN-MANUSIA & MENILAI TIM (36-50) ----------------
    {"id": 36, "sec": 7, "q": "36. Koordinator menetapkan target penyelesaian audit yang menurut perhitungan teknis Anda sangat berat dicapai dengan jumlah personel saat ini. Bagaimana etika Anda dalam merespons atasan?",
     "opts": [
         ("Menerima arahan dengan sikap hormat, lalu berdiskusi secara empat mata menyajikan data kapasitas tim serta mengajukan opsi strategi/dukungan alat agar target dapat tercapai.", 5),
         ("Menyampaikan keluhan kepada anggota tim bahwa target yang diberikan atasan tidak mempertimbangkan kondisi lapangan.", 2),
         ("Menyetujui secara lisan di hadapan atasan tanpa menyampaikan kendala, meski tahu target tersebut tidak akan tercapai.", 1),
         ("Menolak instruksi tersebut secara langsung di grup terbuka karena dinilai membebani tim.", 1)
     ]},
    {"id": 37, "sec": 7, "q": "37. Ketika terjadi kendala teknis rumit di lokasi yang belum pernah ditemui sebelumnya, bagaimana cara terbaik seorang Leader melapor kepada Koordinator?",
     "opts": [
         ("Melapor secara solutif: merangkum data parameter yang sudah diukur, menyebutkan langkah isolasi yang telah dicoba, dan mengajukan 2 alternatif tindakan untuk diputuskan bersama.", 5),
         ("Menunggu hingga Koordinator menanyakan perkembangan pekerjaan baru menyampaikan kendala yang dihadapi.", 2),
         ("Langsung menelepon Koordinator begitu tiba di site tanpa melakukan pengecekan awal sama sekali.", 2),
         ("Menutupi kendala tersebut hingga berlarut-larut karena gengsi meminta arahan teknis.", 1)
     ]},
    {"id": 38, "sec": 7, "q": "38. Koordinator memberikan teguran tegas di grup karena adanya keterlambatan pembaruan laporan progres dari tim Anda. Bagaimana sikap dan balasan Anda?",
     "opts": [
         ("Menerima koreksi secara profesional tanpa berdebat, menyampaikan permohonan maaf, dan segera mengirimkan pembaruan data beserta langkah perbaikan kontrol tim.", 5),
         ("Meminta anggota tim yang bertugas hari itu untuk membalas sendiri pesan teguran dari Koordinator.", 2),
         ("Membalas dengan argumen panjang lebar di grup untuk menyalahkan anggota lapangan yang lambat mengirim foto.", 1),
         ("Membiarkan pesan teguran tersebut tanpa balasan karena merasa tersinggung ditegur di grup.", 1)
     ]},
    {"id": 39, "sec": 7, "q": "39. Anggota tim mengeluhkan aturan baru dari manajemen pusat. Bagaimana Anda memosisikan diri di antara kebijakan atasan dan keluhan bawahan?",
     "opts": [
         ("Menjadi jembatan yang loyal dan komunikatif: menerjemahkan tujuan baik kebijakan manajemen kepada tim secara jernih, sembari merangkum kendala teknis lapangan untuk diberi solusi.", 5),
         ("Mengatakan kepada tim bahwa Anda hanya meneruskan perintah atasan sehingga mereka tidak boleh mengeluh kepada Anda.", 2),
         ("Menggunakan nada ancaman dengan membawa-bawa nama atasan agar bawahan takut bertanya.", 2),
         ("Ikut menyalahkan kebijakan manajemen di depan bawahan agar Anda terlihat dekat dan disukai anggota.", 1)
     ]},
    {"id": 40, "sec": 7, "q": "40. Bagaimana prinsip etika kepemimpinan Anda saat harus memberikan apresiasi keberhasilan maupun koreksi kesalahan kepada bawahan?",
     "opts": [
         ("Memberikan apresiasi dan pujian secara terbuka di depan tim untuk memotivasi bersama, namun melakukan teguran korektif secara empat mata demi menjaga martabat anggota.", 5),
         ("Menghindari pemberian teguran sama sekali meskipun anggota berbuat salah agar suasana tim selalu terasa santai.", 2),
         ("Menegur kesalahan anggota secara keras di depan umum, namun jarang memberikan apresiasi saat target tercapai.", 1),
         ("Mengklaim keberhasilan eksekusi bawahan di lapangan sebagai prestasi pribadi Anda saat melapor ke atasan.", 0)
     ]},
    {"id": 41, "sec": 7, "q": "41. Seorang teknisi junior mengusulkan metode *wiring* dan pelabelan baru yang terbukti memangkas waktu pemeriksaan hingga 30% dibanding cara lama Anda. Bagaimana sikap Anda?",
     "opts": [
         ("Mengapresiasi dan menguji metodenya, menetapkannya sebagai standar baru tim, serta menyebutkan nama teknisi junior tersebut kepada Koordinator sebagai penggagas ide.", 5),
         ("Membiarkan teknisi tersebut menggunakan caranya sendiri tanpa perlu diterapkan kepada anggota tim yang lain.", 2),
         ("Menolak usulan tersebut karena merasa metode lama yang Anda buat sudah tidak perlu diubah oleh junior.", 1),
         ("Mengadopsi metode tersebut lalu mempresentasikannya kepada Koordinator seolah-olah murni hasil pemikiran Anda.", 1)
     ]},
    {"id": 42, "sec": 7, "q": "42. Saat bekerja di lapangan, tim berinteraksi dengan penjaga lahan (warga lokal), petugas keamanan, dan teknisi kebersihan. Sikap apa yang wajib Anda teladankan?",
     "opts": [
         ("Memanusiakan setiap orang dengan sopan dan penuh respek tanpa memandang jabatan, karena kelancaran akses operasional sangat bertumpu pada hubungan sosial yang baik.", 5),
         ("Langsung masuk ke area perangkat tanpa banyak berinteraksi selama kunci akses sudah dipegang oleh tim.", 2),
         ("Bersikap superior dan memerintah penjaga lokasi karena merasa tim teknis memiliki otoritas lebih tinggi.", 1),
         ("Hanya menunjukkan sikap ramah apabila yang ditemui di lokasi adalah pejabat atau pengawas dari kantor pusat.", 1)
     ]},
    {"id": 43, "sec": 7, "q": "43. Tim dari area/cluster tetangga sedang kewalahan menghadapi gangguan beruntun akibat cuaca ekstrem dan meminta bantuan informasi teknis kepada Anda, sementara tugas tim Anda hari itu sudah tuntas. Sikap Anda?",
     "opts": [
         ("Siap membantu berbagi solusi teknis atau dukungan personel atas seizin Koordinator, karena menjaga performansi regional adalah tanggung jawab bersama.", 5),
         ("Menolak memberikan bantuan karena khawatir akan menambah beban kerja tim Anda sendiri.", 1),
         ("Membantu seadanya dengan syarat leader area sebelah memberikan kompensasi pribadi kepada Anda.", 1),
         ("Membiarkan area tetangga gagal mencapai SLA agar tim area Anda terlihat paling unggul saat rapat bulanan.", 0)
     ]},
    {"id": 44, "sec": 7, "q": "44. Dalam menyusun penilaian kinerja (KPI) bulanan untuk setiap individu di tim Anda, indikator apa yang Anda jadikan landasan utama?",
     "opts": [
         ("Kombinasi terukur berbasis data: kecepatan & ketuntasan teknis (SLA), akurasi & ketepatan waktu laporan, kedisiplinan K3, serta integritas kejujuran.", 5),
         ("Memberikan angka penilaian yang rata-rata sama untuk seluruh anggota tim demi menghindari rasa iri.", 2),
         ("Mengutamakan faktor masa kerja (senioritas) sebagai penentu utama tinggi-rendahnya nilai bulanan.", 2),
         ("Menilai berdasarkan tingkat keakraban personal dan seberapa sering anggota tersebut membantu urusan pribadi Anda.", 1)
     ]},
    {"id": 45, "sec": 7, "q": "45. Anggota X jarang berkomentar di grup namun setiap tugas lapangan selalu tuntas, akurat, dan tanpa komplain. Anggota Y sangat vokal di grup namun hasil kerjanya sering menyisakan masalah. Bagaimana Anda menilai keduanya?",
     "opts": [
         ("Memberikan skor tinggi secara objektif kepada Anggota X atas kualitas output kerjanya, sembari membina Anggota Y agar menyelaraskan keaktifan komunikasi dengan ketuntasan kerja.", 5),
         ("Memberikan nilai sedang yang sama kepada keduanya karena masing-masing dianggap memiliki kekurangan.", 2),
         ("Memberikan nilai lebih tinggi kepada Anggota Y karena lebih sering terlihat merespons pesan di grup.", 1),
         ("Menentukan nilai hanya berdasarkan kesan terakhir yang Anda ingat pada akhir bulan.", 1)
     ]},
    {"id": 46, "sec": 7, "q": "46. Seorang teknisi telah berupaya maksimal menuju lokasi gangguan, namun terhambat banjir besar dan jalan putus yang dibuktikan dengan foto/video koordinat valid sehingga tiket melewati SLA. Bagaimana penilaian Anda?",
     "opts": [
         ("Menilai secara proporsional dan adil: tetap mengapresiasi usaha serta kepatuhan pelaporan berkala teknisi, sambil mencatat kendala kahar (force majeure) secara resmi pada berita acara.", 5),
         ("Langsung menarik teknisi tersebut dan menggantinya dengan personel lain tanpa mempertimbangkan kondisi medan.", 2),
         ("Memotong penuh nilai kinerja teknisi tersebut karena hanya berpatokan pada angka akhir SLA semata.", 1),
         ("Menginstruksikan teknisi mengubah jam tiba pada laporan agar seolah-olah tidak terjadi keterlambatan.", 1)
     ]},
    {"id": 47, "sec": 7, "q": "47. Bagaimana metode Anda agar tidak terjebak bias *Recency Effect* (hanya menilai anggota berdasarkan kejadian 2 hari terakhir dan melupakan kinerja konsisten mereka selama 3 minggu sebelumnya)?",
     "opts": [
         ("Membuat catatan log mingguan sederhana (rekap tiket selesai, ketepatan laporan, dan poin kedisiplinan) sehingga evaluasi akhir bulan murni akumulasi data satu bulan penuh.", 5),
         ("Mengandalkan daya ingat secara spontan pada saat formulir penilaian bulanan harus dikumpulkan.", 2),
         ("Meminta pendapat dari salah satu anggota senior mengenai siapa yang layak mendapat nilai tertinggi.", 2),
         ("Memberikan nilai secara bergiliran setiap bulan agar semua anggota pernah merasakan nilai tinggi.", 1)
     ]},
    {"id": 48, "sec": 7, "q": "48. Ketika Anda menyampaikan hasil evaluasi bulanan kepada seorang anggota yang nilainya rendah, ia merasa keberatan dan menuduh Anda tidak adil. Apa tindakan Anda?",
     "opts": [
         ("Membuka data rekam jejak kinerjanya secara transparan (jumlah keterlambatan laporan, tiket berulang, dll.), berdiskusi secara objektif, dan menyepakati target perbaikan bulan depan.", 5),
         ("Mengubah nilainya menjadi lebih tinggi saat itu juga agar tidak terjadi perdebatan panjang.", 1),
         ("Menolak berdiskusi dan menegaskan bahwa penilaian atasan bersifat mutlak tanpa perlu dijelaskan.", 1),
         ("Mengatakan bahwa nilai rendah tersebut merupakan instruksi langsung dari Koordinator.", 1)
     ]},
    {"id": 49, "sec": 7, "q": "49. Dalam mendistribusikan penugasan ke site yang berjarak jauh/medan berat dan site dalam kota yang mudah, bagaimana prinsip keadilan yang Anda terapkan?",
     "opts": [
         ("Mengatur jadwal rotasi dan pembagian beban secara proporsional sesuai kompetensi, serta mencatat histori penugasan agar beban tim terdistribusi merata dan transparan.", 5),
         ("Membiarkan anggota tim memilih dan bernegosiasi sendiri lokasi mana yang ingin mereka datangi.", 2),
         ("Menugaskan lokasi medan berat secara terus-menerus hanya kepada anggota yang jarang mengeluh.", 1),
         ("Memberikan lokasi dalam kota secara rutin kepada anggota yang paling dekat secara personal dengan Anda.", 1)
     ]},
    {"id": 50, "sec": 7, "q": "50. Saat Koordinator memberikan apresiasi kepada Anda atas keberhasilan area Anda meraih peringkat terbaik bulan ini, bagaimana Anda meresponsnya?",
     "opts": [
         ("Mengucapkan terima kasih kepada Koordinator, menyebutkan secara spesifik kontribusi kerja keras anggota tim di lapangan, dan meneruskan apresiasi tersebut ke grup tim.", 5),
         ("Menyampaikan bahwa pencapaian tersebut diraih karena kebetulan bulan ini jarang terjadi gangguan besar.", 2),
         ("Menuntut pemberian bonus tunai seketika itu juga di hadapan rekan-rekan kerja lainnya.", 2),
         ("Menerima pujian tersebut sebagai keberhasilan pribadi Anda sendiri tanpa perlu menyebut peran anggota tim.", 1)
     ]},

    # ---------------- BAGIAN 8: PENALARAN LOGIS & MASALAH KOMPLEKS (51-60) ----------------
    {"id": 51, "sec": 8, "q": "51. Sistem operasional menerapkan aturan logis: 'Pengajuan dana di SIRAPI hanya terbuka jika teknisi sudah menyelesaikan laporan pekerjaan sebelumnya di SIDATA'. Teknisi Rian melapor tidak bisa mengajukan dana padahal sinyal internetnya 4G stabil. Apa langkah pemeriksaan paling logis?",
     "opts": [
         ("Memeriksa status ketuntasan submit laporan pekerjaan terakhir milik Teknisi Rian di aplikasi SIDATA karena penguncian otomatis dipicu oleh laporan yang belum selesai.", 5),
         ("Meminta Admin Operasional melakukan transfer dana secara manual tanpa melalui sistem aplikasi.", 2),
         ("Menyimpulkan bahwa server aplikasi SIRAPI sedang mengalami gangguan massal di seluruh wilayah.", 1),
         ("Menginstruksikan Teknisi Rian mengganti perangkat telepon genggamnya dengan tipe yang lebih baru.", 1)
     ]},
    {"id": 52, "sec": 8, "q": "52. Terdapat 3 lokasi pada satu poros jalan dari Kantor: Site X (km 20, baterai tahan 6 jam), Site Y (km 45, baterai kritis sisa 50 menit), dan Site Z (km 50, jadwal PM rutin). Kecepatan rata-rata mobil tim 60 km/jam. Rute mana yang paling logis dan efisien?",
     "opts": [
         ("Melaju langsung ke Site Y (tiba dalam 45 menit) untuk menyelamatkan site sebelum drop, lanjut 5 km ke Site Z untuk PM, lalu menangani Site X saat perjalanan kembali.", 5),
         ("Menuju Site Z yang paling ujung terlebih dahulu, lalu berurut mundur ke Site Y dan Site X.", 2),
         ("Berhenti mengerjakan Site X terlebih dahulu karena jaraknya paling dekat dari kantor, baru menuju Site Y.", 1),
         ("Bolak-balik kembali ke kantor setiap kali selesai menangani satu lokasi.", 1)
     ]},
    {"id": 53, "sec": 8, "q": "53. Sebuah site selalu mengalami alarm *rectifier module off* dan *high temp* setiap pukul 13.00–14.30 saat cuaca cerah terik, namun kembali normal sendiri setelah pukul 17.00 sore. Tegangan input PLN terukur stabil 222V. Kesimpulan penalaran teknis yang paling tepat adalah:",
     "opts": [
         ("Terjadi kegagalan sirkulasi pendinginan (AC shelter/exhaust fan mati atau filter buntu) sehingga suhu ruang melampaui batas saat puncak panas siang hari dan memicu proteksi termal rectifier.", 5),
         ("Kapasitas baterai stater genset mengalami penurunan tegangan setiap siang hari.", 2),
         ("Jaringan kabel optik mengalami pemuaian di siang hari yang menyebabkan modul rectifier mati.", 1),
         ("Terdapat faktor gangguan non-teknis di sekitar lokasi yang hanya muncul pada siang hari.", 0)
     ]},
    {"id": 54, "sec": 8, "q": "54. Pada laporan BBM, seorang teknisi menginput KM Awal: 62.100 dan KM Akhir: 62.380 (selisih 280 km) untuk perjalanan PP dari Kantor ke Site K. Padahal jarak peta Kantor ke Site K hanya 35 km (PP 70 km). Bagaimana analisis logis Anda?",
     "opts": [
         ("Menahan verifikasi karena terdapat deviasi jarak tidak wajar sebesar 210 km, lalu mencocokkan bukti foto odometer dan koordinat GPS untuk memastikan apakah ada salah ketik, penugasan berantai, atau indikasi manipulasi.", 5),
         ("Memotong nominal pengajuan dana BBM tersebut menjadi separuhnya secara sepihak tanpa mengonfirmasi ke teknisi.", 2),
         ("Langsung menuduh teknisi melakukan pencurian dana di grup tanpa memeriksa bukti foto odometer.", 2),
         ("Menyetujui pengajuan tersebut begitu saja selama total nominal rupiahnya masih terlihat standar.", 1)
     ]},
    {"id": 55, "sec": 8, "q": "55. Sistem baterai 48V di sebuah site mampu mem-backup beban 25 Ampere selama 4 jam penuh. Apabila karena penambahan perangkat baru arus beban meningkat dua kali lipat menjadi 50 Ampere, maka secara logis waktu bertahan (*backup time*) baterai tersebut akan:",
     "opts": [
         ("Turun menjadi sekitar separuhnya (kurang lebih 2 jam atau sedikit di bawahnya akibat faktor pelepasan arus tinggi), sehingga site tersebut harus naik status menjadi prioritas siaga.", 5),
         ("Tetap bertahan selama 4 jam penuh karena jumlah fisik blok baterainya tidak dikurangi.", 1),
         ("Meningkat menjadi 8 jam karena arus yang mengalir lebih besar.", 1),
         ("Menyebabkan seluruh modul rectifier langsung terbakar saat listrik PLN menyala.", 1)
     ]},
    {"id": 56, "sec": 8, "q": "56. Dari evaluasi 25 laporan audit yang dikoreksi bulan ini, ditemukan 20 kesalahan terletak pada kolom 'Pengukuran Arus Beban per Fasa' yang dilakukan oleh 5 teknisi berbeda. Kesimpulan manajerial paling logis dari pola ini adalah:",
     "opts": [
         ("Terdapat ketidaksamaan pemahaman standar cara ukur atau format instruksi kolom yang membingungkan, sehingga solusinya adalah melakukan penyeragaman SOP pengukuran singkat bagi seluruh teknisi.", 5),
         ("Menghapus kolom pengukuran arus beban fasa dari formulir agar tidak ada lagi kesalahan input.", 2),
         ("Menyimpulkan bahwa kelima teknisi tersebut sengaja bersepakat untuk mengacaukan data audit area.", 1),
         ("Mengganti kelima teknisi tersebut secara serentak pada bulan berikutnya.", 1)
     ]},
    {"id": 57, "sec": 8, "q": "57. Dua site yang berjarak hanya 10 menit perjalanan harus diperiksa pada pagi yang sama oleh 2 tim berbeda, namun alat ukur *Battery Conductance Tester* yang berfungsi di kantor hanya ada 1 unit. Pengaturan logis yang paling tepat adalah:",
     "opts": [
         ("Menyinkronkan urutan kerja: Tim 1 langsung melakukan pengetesan baterai di Site A sementara Tim 2 melakukan pembersihan fisik & cek visual di Site B; selesai tes (20 menit), alat langsung digeser ke Site B.", 5),
         ("Menunda pemeriksaan Site B hingga minggu depan sampai kantor membeli alat ukur tambahan.", 2),
         ("Membatalkan kunjungan ke Site B agar Tim 1 leluasa membawa alat ukur seharian penuh.", 1),
         ("Meminta Tim 2 mengisi angka kesehatan baterai di Site B berdasarkan perkiraan visual saja.", 0)
     ]},
    {"id": 58, "sec": 8, "q": "58. Data menunjukkan bahwa setelah Anda memperketat kewajiban 'pengencangan terminasi konektor & uji beban genset 15 menit' saat PM rutin, angka gangguan darurat malam hari turun 65%. Kesimpulan strategis apa yang Anda tarik?",
     "opts": [
         ("Kualitas eksekusi PM berkorelasi langsung dengan keandalan site; menjaga disiplin kualitas PM di siang hari adalah kunci utama mencegah kelelahan tim akibat gangguan malam hari.", 5),
         ("Penurunan gangguan tersebut murni faktor kebetulan karena kondisi jaringan PLN sedang jarang padam.", 2),
         ("Melonggarkan kembali pengawasan PM bulan depan karena jumlah gangguan sudah terbukti berkurang.", 1),
         ("Menyimpulkan bahwa kegiatan PM rutin tidak memiliki kaitan langsung dengan gangguan mendadak.", 1)
     ]},
    {"id": 59, "sec": 8, "q": "59. Anggaran pemeliharaan preventif sisa akhir bulan hanya cukup untuk mengganti suku cadang aus di 1 lokasi: Site Dalam Kota (jarak 15 menit, risiko sedang) atau Site Seberang Sungai (akses 4 jam perjalanan + perahu, komponen sudah kritis). Mana yang Anda pilih?",
     "opts": [
         ("Mendahulukan Site Seberang Sungai, karena secara manajemen risiko, apabila site pedalaman tersebut jatuh mati di malam hari, waktu tempuh, biaya mobilisasi, dan potensi pelanggaran SLA-nya jauh lebih berat.", 5),
         ("Membagi dua dana tersebut sehingga kedua site hanya diperbaiki secara darurat dan tidak tuntas.", 2),
         ("Mendahulukan Site Dalam Kota karena dekat dari kantor dan cepat diselesaikan.", 1),
         ("Menyimpan anggaran tersebut dan tidak memperbaiki keduanya hingga bulan depan.", 1)
     ]},
    {"id": 60, "sec": 8, "q": "60. Apabila Anda resmi dipercaya menjadi Team Leader, indikator kesuksesan paling nyata yang ingin Anda buktikan dalam 6 bulan pertama adalah:",
     "opts": [
         ("Terbangunnya tim yang disiplin mandiri tanpa harus diawasi terus-menerus, akurasi data & kejujuran dana 100%, pencapaian SLA stabil tinggi, serta meningkatnya keahlian teknis seluruh anggota.", 5),
         ("Mengerjakan sendiri seluruh perbaikan sulit di lapangan agar anggota tim tidak perlu repot belajar.", 2),
         ("Menjadi pemimpin yang paling ditakuti oleh anggota dan paling sering dipuji secara pribadi oleh atasan.", 1),
         ("Menghilangkan seluruh aturan disiplin yang ketat agar tidak ada satu pun anggota tim yang mengeluh.", 1)
     ]},

    # ---------------- BAGIAN 9 [BARU]: KEMITRAAN EKSTERNAL & KOMUNIKASI LINTAS PERUSAHAAN (61-75) ----------------
    {"id": 61, "sec": 9, "q": "61. [Komunikasi dengan Maincon/Customer] Saat terjadi gangguan *site down*, PIC dari perusahaan pemberi kerja (Maincon/Operator) menghubungi Anda dengan nada tinggi menuntut site menyala dalam 10 menit, padahal tim masih berjarak 40 menit perjalanan. Bagaimana komunikasi Anda?",
     "opts": [
         ("Merespons dengan tenang dan sopan, menyampaikan posisi koordinat tim secara jujur dan terukur, menjelaskan langkah persiapan yang sudah disiapkan, serta memberikan update berkala setiap 15 menit hingga tiba.", 5),
         ("Menjanjikan site pasti menyala dalam 10 menit agar PIC Customer senang saat itu, meskipun secara teknis mustahil dicapai.", 2),
         ("Membalas dengan nada tinggi bahwa tim tidak bisa terbang dan meminta Customer tidak terus-menerus menelepon.", 1),
         ("Mematikan telepon dan mengabaikan panggilan PIC Customer sampai pekerjaan di lokasi selesai.", 1)
     ]},
    {"id": 62, "sec": 9, "q": "62. [Etika Menjaga Rahasia Perusahaan di Depan Mitra] Saat sedang berdiskusi di lokasi bersama perwakilan perusahaan mitra/klien, mereka menanyakan permasalahan internal kantor Anda (seperti isu keterlambatan dana atau kekurangan personel). Bagaimana sikap Anda?",
     "opts": [
         ("Menjaga kerahasiaan dapur internal perusahaan secara profesional, tetap menampilkan citra kesiapan tim yang solid, dan mengarahkan pembicaraan kembali pada solusi teknis bersama.", 5),
         ("Menceritakan sebagian keluhan internal tim kepada pihak mitra agar mereka bersimpati dan memaklumi jika ada keterlambatan.", 2),
         ("Membongkar seluruh kelemahan manajemen dan admin kantor Anda kepada pihak perusahaan mitra.", 1),
         ("Menolak berbicara sama sekali dengan pihak mitra selama berada di lokasi kerja.", 1)
     ]},
    {"id": 63, "sec": 9, "q": "63. [Kolaborasi Lintas Vendor / Joint Troubleshooting] Sebuah gangguan melibatkan dua pihak: tim Anda (Power/CME) dan tim perusahaan mitra (Transmisi/FO). Di lokasi, tim mitra langsung menuduh sistem power Anda yang bermasalah tanpa melakukan pengecekan. Sikap Anda?",
     "opts": [
         ("Mengajak tim mitra melakukan pengukuran bersama secara objektif di titik batas tanggung jawab (demarkasi): membuktikan tegangan output DC 48V normal dengan alat ukur, lalu membantu mengisolasi titik masalah secara kolaboratif.", 5),
         ("Langsung meninggalkan lokasi begitu melihat indikator rectifier menyala hijau tanpa berkoordinasi dengan tim mitra.", 2),
         ("Terlibat adu mulut di lokasi dan menuduh balik perangkat transmisi mereka yang rusak tanpa bukti ukur.", 1),
         ("Menerima tuduhan tersebut begitu saja dan membongkar panel power meskipun tegangannya terukur normal.", 1)
     ]},
    {"id": 64, "sec": 9, "q": "64. [Koordinasi dengan Tower Provider / Pemilik Lahan] Tim Anda tertahan di gerbang site karena pihak penjaga dari perusahaan Tower Provider menolak membuka kunci dengan alasan Surat Izin Masuk (SIM/SIK) belum terinfo di sistem mereka. Apa langkah Anda?",
     "opts": [
         ("Tetap tenang dan menghormati prosedur keamanan mitra; segera menunjukkan dokumen tugas resmi sambil menghubungi PIC Tower Provider/Admin untuk sinkronisasi izin akses tanpa memicu keributan di lokasi.", 5),
         ("Memutuskan langsung pulang ke kantor dan membatalkan penanganan gangguan hari itu juga.", 2),
         ("Memaksa masuk dengan cara merusak gembok gerbang milik perusahaan Tower Provider agar cepat selesai.", 1),
         ("Memarahi dan mengancam penjaga site karena menghalangi pekerjaan darurat tim Anda.", 1)
     ]},
    {"id": 65, "sec": 9, "q": "65. [Manajemen Subkon / Vendor Lokal] Perusahaan Anda menugaskan vendor/bengkel rekanan untuk melakukan servis besar genset di sebuah site. Sebagai Leader area, bagaimana cara Anda mengawasi pekerjaan mitra vendor tersebut?",
     "opts": [
         ("Memastikan ruang lingkup kerja (Scope of Work) jelas, memverifikasi keaslian suku cadang yang diganti, serta melakukan uji beban (load test) bersama sebelum menandatangani Berita Acara selesai.", 5),
         ("Langsung menandatangani Berita Acara pekerjaan vendor di kantor hanya berdasarkan foto kiriman mereka tanpa verifikasi fungsi.", 2),
         ("Menyerahkan sepenuhnya kepada pihak vendor tanpa pengawasan karena menganggap itu sudah tanggung jawab mereka.", 1),
         ("Mencari-cari kesalahan yang tidak ada di kontrak untuk menghambat pembayaran tagihan vendor tersebut.", 1)
     ]},
    {"id": 66, "sec": 9, "q": "66. [Permintaan di Luar Kontrak / Out of Scope dari Mitra] Saat di lapangan, pengawas dari perusahaan mitra meminta tim Anda mengerjakan pekerjaan tambahan berat yang berada di luar kontrak kerja dan membutuhkan biaya material tambahan. Sikap Anda?",
     "opts": [
         ("Menyampaikan secara sopan dan diplomatis bahwa tim siap membantu, namun karena berdampak pada material dan lingkup kontrak, Anda perlu mengonfirmasi persetujuan Koordinator terlebih dahulu agar resmi tercatat.", 5),
         ("Langsung memerintahkan tim mengerjakannya menggunakan dana operasional tim sendiri demi menyenangkan pengawas mitra.", 2),
         ("Menolak dengan kalimat ketus bahwa tim Anda bukan bawahan mereka dan tidak mau disuruh-suruh.", 1),
         ("Menyetujui permintaan tersebut dengan meminta bayaran uang tunai langsung ke kantong pribadi Anda.", 0)
     ]},
    {"id": 67, "sec": 9, "q": "67. [Koordinasi Eksternal dengan Pihak PLN] Sebuah site mengalami putus fasa (1 fasa mati) dari jaringan tiang luar milik PLN sehingga rectifier tidak bekerja optimal. Bagaimana cara Anda membangun komunikasi dengan petugas gangguan PLN setempat?",
     "opts": [
         ("Menghubungi saluran resmi dan berkoordinasi secara santun dengan petugas teknis PLN di lapangan, memberikan informasi titik gardu/tiang yang jelas serta nomor ID pelanggan untuk mempercepat pemulihan.", 5),
         ("Menunggu pasif di dalam site selama berhari-hari sampai pihak PLN menyadari sendiri adanya fasa yang putus.", 2),
         ("Memerintahkan teknisi Anda memanjat tiang jaringan tegangan rendah milik PLN secara ilegal untuk menyambung sendiri.", 1),
         ("Menegur petugas lapangan PLN dengan nada menyalahkan karena listrik mereka sering bermasalah.", 1)
     ]},
    {"id": 68, "sec": 9, "q": "68. [Negosiasi Teknis & Klaim Berita Acara ke Mitra] Pihak perusahaan pemberi kerja menolak klaim *Force Majeure* (bebas penalti SLA) atas keterlambatan tim Anda yang terjebak pohon tumbang, karena dokumentasi yang dikirim anggota Anda kurang lengkap. Langkah Anda?",
     "opts": [
         ("Menyusun kronologi waktu (timeline) yang rapi, melengkapi bukti pendukung (titik koordinat GPS, timestamp foto, keterangan warga/aparat setempat), dan mempresentasikannya secara profesional bersama Koordinator.", 5),
         ("Pasrah menerima penolakan tersebut tanpa berusaha melengkapi bukti yang diminta oleh pihak mitra.", 2),
         ("Menyalahkan pihak mitra secara emosional karena dianggap tidak memiliki rasa kemanusiaan.", 1),
         ("Membuat foto rekayasa di lokasi lain pada hari berikutnya untuk mengelabui pihak mitra.", 0)
     ]},
    {"id": 69, "sec": 9, "q": "69. [Menjaga Reputasi & Standar K3 di Hadapan Klien] Saat tim Anda sedang bekerja di site, tiba-tiba tim manajemen dari perusahaan Klien/Maincon datang melakukan inspeksi mendadak (*sidak*). Apa yang mencerminkan kualitas kepemimpinan Anda?",
     "opts": [
         ("Tim terlihat bekerja tertib menggunakan APD lengkap, area kerja bersih dan aman, serta Anda mampu menjelaskan parameter teknis site secara lugas dan ramah mewakili perusahaan.", 5),
         ("Segera menyembunyikan peralatan yang tidak standar dan meminta anggota tim menghindar dari area sidak.", 2),
         ("Membiarkan anggota tetap bekerja tanpa APD sambil beralasan kepada klien bahwa cuaca sedang panas.", 1),
         ("Menolak kedatangan tim sidak klien karena tidak memberikan pemberitahuan sehari sebelumnya.", 1)
     ]},
    {"id": 70, "sec": 9, "q": "70. [Penyelesaian Sengketa Kerusakan Aset Mitra] Anggota tim Anda tidak sengaja mematahkan engsel pintu panel milik mitra vendor lain saat sedang bekerja di shelter yang sempit. Bagaimana sikap kemitraan yang berintegritas?",
     "opts": [
         ("Melaporkan kejadian tersebut secara jujur kepada Koordinator dan PIC mitra terkait, serta segera melakukan perbaikan/penggantian engsel yang rusak sebagai bentuk tanggung jawab profesional.", 5),
         ("Mengikat engsel yang patah dengan kawat seadanya tanpa memberitahu pihak pemilik panel.", 2),
         ("Menutup pintu panel rapat-rapat dan berharap tim vendor yang datang minggu depan yang akan disalahkan.", 1),
         ("Menuduh tim mitra sebelumnya yang telah merusak engsel tersebut saat ditanya oleh pengawas.", 0)
     ]},
    {"id": 71, "sec": 9, "q": "71. [Komunikasi Tertulis / Email & Grup Gabungan Mitra] Ketika Anda tergabung di dalam grup WhatsApp resmi yang berisi Koordinator, manajemen perusahaan Anda, dan pihak Klien/Maincon, bagaimana standar komunikasi yang Anda terapkan?",
     "opts": [
         ("Menggunakan bahasa Indonesia yang baku, sopan, berbasis data ukur yang terverifikasi, serta tidak pernah memperdebatkan masalah internal tim di dalam grup gabungan tersebut.", 5),
         ("Menjawab pesan klien hanya dengan singkatan singkat seadanya tanpa melampirkan data pendukung.", 2),
         ("Menegur dan memarahi kesalahan anggota tim Anda secara langsung di dalam grup gabungan bersama klien tersebut.", 1),
         ("Mengirimkan keluhan mengenai keterlambatan uang operasional internal ke dalam grup yang berisi pihak klien.", 0)
     ]},
    {"id": 72, "sec": 9, "q": "72. [Evaluasi Kinerja Mitra Subkon] Di wilayah Anda terdapat dua mitra penyedia sewa genset harian. Mitra A harganya sedikit lebih murah namun unitnya sering mogok di lokasi, sedangkan Mitra B harganya standar sesuai plafon namun unitnya selalu prima dan tepat waktu. Analisis rekomendasi Anda ke Koordinator?",
     "opts": [
         ("Merekomendasikan Mitra B dengan menyajikan data perbandingan *Total Cost & Risk*: unit Mitra A yang sering mogok justru memicu risiko denda SLA dan biaya lembur teknisi yang jauh lebih mahal.", 5),
         ("Tetap memilih Mitra A semata-mata karena angka sewa hariannya terlihat paling murah di atas kertas.", 2),
         ("Menggunakan kedua mitra secara bergantian tanpa mencatat histori keandalan unit masing-masing.", 2),
         ("Memilih mitra mana pun yang bersedia memberikan komisi pribadi kepada tim lapangan.", 0)
     ]},
    {"id": 73, "sec": 9, "q": "73. [Sinergi Berbagi Informasi dengan Mitra Sektor Lain] Tim mitra pemeliharaan jaringan fiber optik mengabarkan kepada Anda bahwa di Km 32 arah site Anda sedang ada perbaikan jembatan yang menutup akses mobil. Bagaimana Anda merespons kemitraan ini?",
     "opts": [
         ("Mengucapkan terima kasih atas informasinya, segera menyesuaikan rencana rute/moda transportasi tim Anda, dan aktif berbagi informasi kondisi power/akses site sebaliknya yang bermanfaat bagi tim mereka.", 5),
         ("Membaca pesan tersebut tanpa membalas dan tetap memaksakan mobil melewati jalur yang ditutup.", 2),
         ("Mengabaikan informasi dari perusahaan lain karena merasa tim sendiri lebih hafal jalan.", 1),
         ("Menyuruh tim batal berangkat bekerja hari itu dengan alasan jembatan sedang diperbaiki.", 1)
     ]},
    {"id": 74, "sec": 9, "q": "74. [Ketegasan Menghadapi Oknum Mitra yang Mengajak Kecurangan] Seorang oknum pengawas dari perusahaan mitra mengajak Anda bekerja sama memalsukan laporan jam nyala genset (*running hours*) agar selisih klaim solarnya dibagi dua. Sikap Anda?",
     "opts": [
         ("Menolak dengan tegas tanpa kompromi, menjaga keakuratan data riil sesuai foto hour-meter, dan melaporkan upaya kecurangan tersebut secara tertutup kepada Koordinator.", 5),
         ("Menolak ikut menikmati uangnya, namun membiarkan oknum tersebut mengubah angkanya sendiri di laporan.", 2),
         ("Menyetujui ajakan tersebut karena merasa yang dirugikan adalah perusahaan mitra, bukan perusahaan Anda.", 0),
         ("Mengikuti kemauan oknum tersebut karena takut dipersulit saat proses verifikasi pekerjaan berikutnya.", 1)
     ]},
    {"id": 75, "sec": 9, "q": "75. [Membangun Kepercayaan Jangka Panjang dengan Mitra] Apa kunci utama agar perusahaan tempat Anda bekerja selalu dipercaya dan mendapatkan penilaian kinerja tertinggi (*Vendor Performance Evaluation*) dari pihak Pemberi Kerja?",
     "opts": [
         ("Konsistensi antara kecepatan respons lapangan, ketuntasan perbaikan teknis (*zero repeat trouble*), transparansi komunikasi saat krisis, dan keakuratan dokumen laporan.", 5),
         ("Sering memberikan janji-janji manis kepada pihak pemberi kerja meskipun realisasi di lapangan sering meleset.", 2),
         ("Hanya fokus memperbaiki site yang berada di dekat kantor pusat pemberi kerja saja.", 1),
         ("Mengandalkan hubungan pertemanan pribadi semata tanpa menjaga pencapaian SLA teknis.", 1)
     ]},

    # ---------------- BAGIAN 10 [BARU]: MATEMATIKA POWER & ANALOGI TEKNIS (76-90) ----------------
    {"id": 76, "sec": 10, "q": "76. [Hitungan Daya DC ke AC] Sebuah site telekomunikasi memiliki beban sistem DC yang terukur pada layar Rectifier sebesar **50 Volt** dengan arus beban total **44 Ampere**. Jika diasumsikan efisiensi konversi sempurna (100%) pada tegangan PLN **220 Volt AC**, berapakah daya beban tersebut dan berapa arus AC yang mengalir?",
     "opts": [
         ("Daya beban = 2.200 Watt (2,2 kW) dan arus input AC yang mengalir sebesar 10 Ampere.", 5),
         ("Daya beban = 1.800 Watt (1,8 kW) dan arus input AC yang mengalir sebesar 8 Ampere.", 2),
         ("Daya beban = 2.200 Watt (2,2 kW) dan arus input AC yang mengalir sebesar 44 Ampere.", 1),
         ("Daya beban = 4.400 Watt (4,4 kW) dan arus input AC yang mengalir sebesar 20 Ampere.", 1)
     ]},
    {"id": 77, "sec": 10, "q": "77. [Analogi Tangki Air & Backup Time Baterai] Sebuah site dilengkapi 2 bank baterai 48V yang dirangkai paralel, masing-masing berkapasitas **100 Ah** (Total kapasitas = **200 Ah**). Jika batas aman pengurasan (*Depth of Discharge* / DoD) ditetapkan **80%** dari kapasitas total dan beban rata-rata site adalah **32 Ampere**, berapa jam baterai tersebut sanggup mem-backup?",
     "opts": [
         ("Kapasitas aman terpakai = 160 Ah, sehingga baterai sanggup bertahan selama 5 jam (160 Ah / 32 A).", 5),
         ("Kapasitas aman terpakai = 200 Ah, sehingga baterai sanggup bertahan selama 6,25 jam (200 Ah / 32 A).", 2),
         ("Kapasitas aman terpakai = 80 Ah, sehingga baterai sanggup bertahan selama 2,5 jam (80 Ah / 32 A).", 1),
         ("Kapasitas aman terpakai = 160 Ah, sehingga baterai sanggup bertahan selama 8 jam.", 1)
     ]},
    {"id": 78, "sec": 10, "q": "78. [Hitungan Redundansi Modul Rectifier N+1] Beban puncak (termasuk arus pengisian baterai) di sebuah site adalah **90 Ampere**. Setiap 1 keping modul rectifier yang terpasang memiliki kapasitas arus maksimal **30 Ampere**. Agar memenuhi standar keamanan redundansi **$N+1$** (jumlah modul penopang beban ditambah 1 modul cadangan aktif), berapa minimal modul rectifier sehat yang wajib terpasang?",
     "opts": [
         ("Minimal 4 modul rectifier (3 modul untuk menopang beban 90A + 1 modul sebagai cadangan redundansi N+1).", 5),
         ("Minimal 3 modul rectifier karena 3 x 30A sudah pas mencapai angka 90 Ampere.", 2),
         ("Minimal 2 modul rectifier karena masing-masing modul bisa dipaksa bekerja di atas 150%.", 1),
         ("Minimal 6 modul rectifier (dua kali lipat dari kebutuhan beban utama).", 2)
     ]},
    {"id": 79, "sec": 10, "q": "79. [Hitungan Konsumsi BBM Genset] Sebuah genset site memiliki tangki harian berisi **65 Liter** solar. Rata-rata konsumsi BBM genset tersebut pada beban normal adalah **2,5 Liter per jam**. Demi mencegah mesin masuk angin, disisakan batas aman **15 Liter** solar di dasar tangki yang tidak boleh terhisap habis. Berapa jam durasi operasi efektif genset tersebut?",
     "opts": [
         ("Volume solar efektif = 50 Liter (65L - 15L), sehingga genset dapat beroperasi aman selama 20 jam (50L / 2,5L).", 5),
         ("Volume solar efektif = 65 Liter, sehingga genset dapat beroperasi selama 26 jam penuh (65L / 2,5L).", 2),
         ("Volume solar efektif = 50 Liter, sehingga genset dapat beroperasi selama 15 jam.", 1),
         ("Volume solar efektif = 40 Liter, sehingga genset dapat beroperasi selama 16 jam.", 1)
     ]},
    {"id": 80, "sec": 10, "q": "80. [Penyeimbangan Beban 3 Fasa R-S-T] Pada panel ACPDB 3 fasa dengan MCB utama 32A per fasa, terukur arus beban yang pincang: **Fasa R = 30 Ampere**, **Fasa S = 9 Ampere**, dan **Fasa T = 9 Ampere**, sehingga Fasa R panas dan rawan trip. Jika Anda menata ulang pembagian beban secara merata ke ketiga fasa, berapa arus ideal pada masing-masing fasa?",
     "opts": [
         ("Total arus 48 Ampere dibagi merata ke 3 fasa, sehingga masing-masing fasa (R, S, T) menanggung 16 Ampere yang jauh lebih dingin dan aman.", 5),
         ("Masing-masing fasa akan menanggung 24 Ampere setelah digabungkan.", 2),
         ("Arus pada Fasa R tetap 30 Ampere, sedangkan Fasa S dan T dinaikkan menjadi 30 Ampere.", 1),
         ("Total arus dibagi dua menjadi 19,5 Ampere pada setiap jalur fasa.", 1)
     ]},
    {"id": 81, "sec": 10, "q": "81. [Konversi kVA ke kW & Batas Aman Beban Genset] Sebuah unit genset memiliki kapasitas tertulis **10 kVA** dengan faktor daya ($\cos \phi$) = **0,8**. Apabila SOP menetapkan pembebanan kontinu maksimal yang aman adalah **80%** dari kapasitas daya aktif murni (kW), berapakah beban maksimal (dalam kW) yang boleh ditanggung genset tersebut?",
     "opts": [
         ("Daya murni 10 kVA x 0,8 = 8 kW; dengan batas aman 80% dari 8 kW, maka beban kontinu maksimal yang aman adalah 6,4 kW (6.400 Watt).", 5),
         ("Beban kontinu maksimal adalah 8 kW penuh karena sudah dikalikan dengan faktor daya 0,8.", 3),
         ("Beban kontinu maksimal adalah 10 kW sesuai angka kVA yang tertera pada pelat nama mesin.", 1),
         ("Beban kontinu maksimal adalah 4,5 kW setelah dikurangi rugi-rugi mekanis.", 2)
     ]},
    {"id": 82, "sec": 10, "q": "82. [Analogi Tegangan Jatuh / Voltage Drop Kabel] Sebuah site memiliki tarikan kabel AC sepanjang 180 meter dari kWh meter ke shelter. Tegangan di kWh meter terukur **225 Volt**, namun sesampainya di panel shelter tegangan turun menjadi **195 Volt** (drop **30 Volt**) saat mengalirkan arus **10 Ampere**. Berapa daya listrik yang terbuang sia-sia menjadi panas di sepanjang kabel tersebut?",
     "opts": [
         ("Daya terbuang di kabel = Rugi Tegangan x Arus = 30 Volt x 10 Ampere = 300 Watt terus-menerus.", 5),
         ("Daya terbuang di kabel = 195 Volt x 10 Ampere = 1.950 Watt.", 2),
         ("Daya terbuang di kabel hanya 30 Watt sesuai angka penurunan tegangannya.", 1),
         ("Tidak ada daya yang terbuang selama perangkat di dalam shelter masih bisa menyala.", 1)
     ]},
    {"id": 83, "sec": 10, "q": "83. [Kalkulasi Arus Beban + Arus Charging Baterai] Beban peralatan aktif di sebuah site adalah **35 Ampere DC**. Di site tersebut terpasang baterai kapasitas **200 Ah** yang baru saja terkuras saat mati lampu. Ketika listrik PLN menyala kembali, baterai menarik arus pengisian (*charging*) sebesar **10% dari kapasitasnya (0,1C)**. Berapa total arus output yang harus disuplai oleh Rectifier pada saat itu?",
     "opts": [
         ("Total arus Rectifier = 35A (beban peralatan) + 20A (arus charging 10% dari 200Ah) = 55 Ampere.", 5),
         ("Total arus Rectifier tetap 35 Ampere karena pengisian baterai tidak mengambil arus dari rectifier.", 1),
         ("Total arus Rectifier = 35A + 200A = 235 Ampere.", 1),
         ("Total arus Rectifier = 35A + 10A = 45 Ampere.", 2)
     ]},
    {"id": 84, "sec": 10, "q": "84. [Analogi Kesehatan Baterai / State of Health (SoH)] Sebuah modul baterai Lithium 48V memiliki kapasitas desain awal **100 Ah**. Hasil pembacaan BMS menunjukkan kesehatan baterai (**SoH**) saat ini tinggal **60%**, meskipun indikator terisi penuh (**SoC 100%**). Jika listrik padam dan baterai menanggung beban konstan **15 Ampere**, berapa lama baterai tersebut akan bertahan sampai habis?",
     "opts": [
         ("Kapasitas riil tersisa = 60% x 100 Ah = 60 Ah; dengan beban 15 Ampere, baterai akan bertahan selama 4 jam (60 Ah / 15 A).", 5),
         ("Karena SoC tertulis 100%, maka kapasitasnya tetap 100 Ah dan bertahan selama 6,6 jam (100 Ah / 15 A).", 2),
         ("Baterai hanya akan bertahan selama 1,5 jam karena SoH sudah di bawah 80%.", 1),
         ("Baterai akan bertahan selama 6 jam penuh tanpa terpengaruh nilai SoH.", 1)
     ]},
    {"id": 85, "sec": 10, "q": "85. [Matematika Rasio BBM Mobil Operasional] Standar konsumsi BBM mobil tim ditetapkan **1 Liter untuk 10 km**, dengan harga BBM **Rp 10.000/Liter**. Tim ditugaskan berangkat dari kantor ke Site A (jarak 65 km), lanjut dari Site A ke Site B (jarak 25 km), lalu kembali dari Site B langsung ke kantor (jarak 80 km), ditambah alokasi mesin menyala stasioner 2 Liter. Berapa total dana BBM yang tepat?",
     "opts": [
         ("Total jarak tempuh = 170 km (17 Liter) + 2 Liter stasioner = 19 Liter x Rp 10.000 = Rp 190.000.", 5),
         ("Total jarak tempuh = 90 km (9 Liter) + 2 Liter stasioner = 11 Liter x Rp 10.000 = Rp 110.000.", 2),
         ("Total jarak tempuh = 260 km (26 Liter) x Rp 10.000 = Rp 260.000.", 1),
         ("Total dana dibulatkan langsung menjadi Rp 300.000 tanpa perlu menghitung rincian jarak antar-site.", 1)
     ]},
    {"id": 86, "sec": 10, "q": "86. [Perhitungan Kapasitas MCB & Safety Margin 125%] Akan dipasang perangkat baru berdaya **960 Watt** pada sistem tegangan **48 Volt DC**. Sesuai standar kelistrikan, ukuran MCB pelindung harus memiliki *safety margin* minimal **125% (1,25 kali)** dari arus beban normal agar MCB tidak panas dan *nuisance trip*. Berapa arus beban perangkat dan ukuran MCB yang tepat?",
     "opts": [
         ("Arus beban = 960W / 48V = 20 Ampere; kebutuhan minimal MCB = 20A x 1,25 = 25A, sehingga dipilih MCB DC 25A atau 32A.", 5),
         ("Arus beban = 960W / 48V = 20 Ampere, sehingga dipasang MCB DC 16A agar cepat memutus arus.", 1),
         ("Arus beban = 960W / 220V = 4,3 Ampere, sehingga cukup dipasang MCB 6A.", 1),
         ("Arus beban = 20 Ampere, namun dipasang MCB 100A agar tidak pernah trip sama sekali.", 2)
     ]},
    {"id": 87, "sec": 10, "q": "87. [Analogi Rangkaian Seri vs Paralel Aki 12V] Di gudang tersedia 4 blok baterai VRLA yang masing-masing bertegangan **12 Volt** dan berkapasitas **100 Ah**. Untuk menyuplai sistem rectifier yang membutuhkan tegangan kerja **48 Volt DC**, bagaimana cara merangkai keempat blok baterai tersebut dan berapa kapasitas totalnya?",
     "opts": [
         ("Dirangkai secara SERI (kutub positif ke negatif berurutan) sehingga tegangannya menjadi 48 Volt (4 x 12V) dengan kapasitas arus tetap 100 Ah.", 5),
         ("Dirangkai secara PARALEL keempatnya sehingga menghasilkan tegangan 48 Volt dengan kapasitas 400 Ah.", 2),
         ("Dirangkai secara SERI sehingga menghasilkan tegangan 48 Volt sekaligus melipatgandakan kapasitasnya menjadi 400 Ah.", 2),
         ("Dirangkai 2 Seri dan 2 Paralel sehingga menghasilkan tegangan 48 Volt 200 Ah.", 1)
     ]},
    {"id": 88, "sec": 10, "q": "88. [Kalkulasi Kebocoran Biaya Listrik kWh] Sebuah unit AC pendingin shelter berdaya **1,5 kW (1.500 Watt)** mengalami kerusakan termostat sehingga kompresornya menyala terus-menerus **24 jam sehari** (normalnya bekerja efektif 12 jam sehari). Jika tarif listrik **Rp 1.500 per kWh**, berapa pemborosan biaya listrik di 1 site tersebut dalam **30 hari**?",
     "opts": [
         ("Pemborosan = 12 jam berlebih x 1,5 kW = 18 kWh/hari x 30 hari = 540 kWh x Rp 1.500 = Rp 810.000 per bulan di satu site.", 5),
         ("Pemborosan = 24 jam x 1,5 kW = 36 kWh x Rp 1.500 = Rp 54.000 per bulan.", 2),
         ("Pemborosan = 1,5 kW x 30 hari x Rp 1.500 = Rp 67.500 per bulan.", 1),
         ("Tidak meningkatkan tagihan listrik karena daya AC tetap 1,5 kW.", 1)
     ]},
    {"id": 89, "sec": 10, "q": "89. [Hitungan Waktu Mobilisasi MBP vs Sisa Ketahanan Baterai] Listrik PLN di Site M padam tepat pukul **09.00 WIB** dan kapasitas baterai di lokasi tersebut hanya sanggup bertahan selama **3 jam (sampai pukul 12.00 WIB)**. Tim genset mobile (MBP) berangkat dari *homebase* yang berjarak **90 km** pada pukul **09.30 WIB** dengan kecepatan rata-rata **45 km/jam**, serta butuh waktu **15 menit** untuk gelar kabel dan *start* genset. Bagaimana kesimpulan matematisnya?",
     "opts": [
         ("Waktu tempuh 90km / 45km/jam = 2 jam (tiba pukul 11.30) + 15 menit instalasi = genset menyala pukul 11.45 WIB; site berhasil diselamatkan 15 menit sebelum baterai habis.", 5),
         ("Waktu tempuh 1 jam (tiba pukul 10.30) sehingga masih tersisa waktu aman 1,5 jam.", 2),
         ("Tim baru tiba pukul 12.30 WIB sehingga site sudah dipastikan mengalami down selama 30 menit.", 2),
         ("Baterai akan habis pada pukul 11.00 WIB sebelum tim mencapai setengah perjalanan.", 1)
     ]},
    {"id": 90, "sec": 10, "q": "90. [Analogi Penurunan Umur Pakai Baterai Akibat Suhu] Secara kaidah teknis baterai, setiap kenaikan suhu ruang sebesar **10°C** di atas suhu standar **25°C** akan memotong umur desain (*lifetime*) baterai menjadi **separuhnya (50%)**. Apabila baterai dengan umur desain **4 tahun** (pada suhu 25°C) dibiarkan bekerja terus-menerus di dalam kabinet yang panas bersuhu **45°C** (naik 20°C / dua kali lipat kenaikan 10°C), berapa estimasi umur pakai baterai tersebut sebelum rusak?",
     "opts": [
         ("Kenaikan pertama (35°C) memotong umur jadi 2 tahun, kenaikan kedua (45°C) memotong separuhnya lagi menjadi hanya sekitar 1 tahun.", 5),
         ("Umur baterai berkurang 10% saja menjadi 3,6 tahun.", 2),
         ("Umur baterai tetap bertahan 4 tahun selama tegangan charging rectifier tidak berubah.", 1),
         ("Umur baterai berkurang menjadi 3 tahun.", 2)
     ]},

    # ---------------- BAGIAN 11 [BARU]: POLA PIKIR DANA, RISIKO & BISNIS PERUSAHAAN (91-100) ----------------
    {"id": 91, "sec": 11, "q": "91. [Pola Pikir Efisiensi Dana Operasional] Bagaimana cara seorang Team Leader yang berorientasi bisnis memandang setiap rupiah dana operasional (BBM, material, akomodasi) yang diajukan oleh timnya?",
     "opts": [
         ("Memandang dana operasional sebagai modal kerja perusahaan yang harus menghasilkan ketuntasan teknis maksimal sekali jalan (*first-time right*), mencegah kerja ulang yang membengkakkan biaya dua kali lipat.", 5),
         ("Memandang dana operasional sebagai jatah anggaran yang harus dihabiskan semaksimal mungkin setiap bulannya.", 1),
         ("Menekan pengajuan dana secara ekstrem hingga melarang tim berangkat ke lokasi gangguan agar terlihat hemat.", 2),
         ("Menyerahkan sepenuhnya urusan efisiensi biaya kepada bagian keuangan tanpa perlu dikontrol oleh Leader lapangan.", 2)
     ]},
    {"id": 92, "sec": 11, "q": "92. [Kalkulasi Risiko Penalti SLA vs Biaya Preventif] Berdasarkan kontrak bisnis perusahaan dengan Maincon, satu kali insiden *Site Down* di lokasi VIP akan dikenakan denda penalti **Rp 5.000.000**. Saat inspeksi, ditemukan kipas panel dan kontaktor yang mulai aus dengan biaya penggantian preventif hanya **Rp 350.000**. Bagaimana pola pikir risiko bisnis Anda?",
     "opts": [
         ("Segera mengajukan penggantian preventif senilai Rp 350.000 tersebut dengan menyajikan analisis risiko bahwa biaya pencegahan hanya 7% dibanding potensi kerugian denda Rp 5.000.000 jika dibiarkan rusak.", 5),
         ("Menunggu sampai kontaktor tersebut benar-benar putus dan menyebabkan site mati agar pengajuan dananya berstatus darurat.", 2),
         ("Mengabaikan temuan tersebut demi menghemat pengeluaran Rp 350.000 pada laporan minggu ini.", 1),
         ("Mengganti komponen tersebut menggunakan barang bekas yang sudah tidak layak pakai.", 1)
     ]},
    {"id": 93, "sec": 11, "q": "93. [Dampak Akumulasi Kebocoran Kecil terhadap Bisnis] Seorang anggota menganggap selisih pembulatan atau mark-up dana BBM sebesar **Rp 25.000 per tiket** adalah hal sepele. Jika dalam 1 bulan terdapat **200 tiket** di satu area, bagaimana Anda menjelaskan dampak bisnisnya?",
     "opts": [
         ("Menjelaskan secara matematis bahwa kebocoran Rp 25.000 x 200 tiket = Rp 5.000.000/bulan atau Rp 60.000.000/tahun di satu area, yang dapat menggerus arus kas perusahaan dan mengancam keberlangsungan kontrak kerja seluruh tim.", 5),
         ("Membiarkan hal tersebut karena nominal Rp 25.000 per transaksi memang terlihat kecil.", 1),
         ("Hanya menegur secara lisan tanpa menghitung dampak akumulasi tahunannya.", 2),
         ("Meminta anggota membatasi pembulatan menjadi Rp 15.000 saja per tiket.", 1)
     ]},
    {"id": 94, "sec": 11, "q": "94. [Strategi Bundling Rute & Penghematan Opex] Pada minggu ini terdapat jadwal: (1) PM Rutin di Site A, (2) Audit Power di Site B yang berjarak 4 km dari Site A, dan (3) Perbaikan pintu pagar di Site A. Ketiganya berjarak 70 km dari kantor. Bagaimana pengaturan bisnis paling efisien?",
     "opts": [
         ("Menggabungkan (bundling) ketiga pekerjaan tersebut dalam 1 kali pemberangkatan terpadu dengan persiapan alat lengkap, sehingga menghemat hingga 66% biaya BBM dan waktu kerja tim.", 5),
         ("Memberangkatkan 3 tim berbeda pada 3 hari yang berlainan sesuai kategori tiket masing-masing.", 2),
         ("Mengerjakan PM Rutin saja minggu ini dan menunda dua pekerjaan lainnya ke bulan depan.", 2),
         ("Mengajukan tiga kali anggaran BBM penuh secara terpisah meskipun dikerjakan dalam satu kali perjalanan.", 0)
     ]},
    {"id": 95, "sec": 11, "q": "95. [Manajemen Risiko Kerugian Hukum & Klaim Pihak Ketiga] Mengapa seorang Leader wajib bersikap cerewet dan tegas terkait K3, pengamanan kelistrikan, serta ketertiban berkendara mobil operasional?",
     "opts": [
         ("Karena satu kecelakaan kerja atau kelalaian yang merusak properti pihak ketiga tidak hanya membahayakan nyawa, tetapi juga menimbulkan kerugian biaya klaim puluhan juta rupiah serta sanksi pembekuan izin kerja perusahaan.", 5),
         ("Semata-mata hanya untuk menggugurkan kewajiban administrasi pengisian formulir K3 harian.", 2),
         ("Agar terlihat berwibawa saat memarahi anggota tim sebelum berangkat.", 1),
         ("Hanya perlu diperketat pada saat ada kunjungan pengawas dari kantor pusat saja.", 1)
     ]},
    {"id": 96, "sec": 11, "q": "96. [Pola Pikir Menjaga Aset Perusahaan (Capex/Opex)] Bagaimana tanggung jawab finansial seorang Leader terhadap aset inventaris tim seperti mobil operasional, genset portable, tang ampere, dan toolkit?",
     "opts": [
         ("Menerapkan jadwal perawatan berkala dan penanggung jawab per alat, karena menjaga keawetan aset sama dengan mencegah pengeluaran biaya servis besar dan menjaga kelancaran operasional.", 5),
         ("Menggunakan peralatan dan kendaraan secara paksa tanpa perawatan rutin karena merasa biaya servis ditanggung perusahaan.", 1),
         ("Menyimpan seluruh alat ukur baru di lemari rumah dan melarang tim memakainya di lapangan agar tidak rusak.", 2),
         ("Baru memeriksa kondisi aset apabila sudah ada alat yang hilang atau mobil mogok total.", 2)
     ]},
    {"id": 97, "sec": 11, "q": "97. [Hubungan Kualitas Laporan dengan Cashflow / Penagihan Perusahaan] Mengapa keterlambatan atau ketidaklengkapan foto eviden pada laporan PM/Troubleshooting sangat merugikan kesehatan finansial perusahaan?",
     "opts": [
         ("Karena dokumen Berita Acara dan eviden yang cacat/terlambat akan menahan proses penagihan invoice (*billing*) perusahaan ke Pemberi Kerja, padahal perusahaan sudah mengeluarkan uang tunai duluan untuk gaji dan BBM.", 5),
         ("Karena laporan foto hanya berfungsi untuk memenuhi memori penyimpanan Google Drive kantor.", 1),
         ("Tidak berdampak pada keuangan perusahaan selama perangkat di lapangan sudah diperbaiki.", 1),
         ("Hanya berdampak pada beban kerja Admin Operasional semata.", 2)
     ]},
    {"id": 98, "sec": 11, "q": "98. [Pengambilan Keputusan Repair vs Replace] Sebuah unit genset mobile tua mengalami kerusakan komponen yang sama hingga 4 kali dalam sebulan, menghamburkan biaya panggil teknisi dan BBM sebesar Rp 1.600.000, sementara harga penggantian komponen baru satu set secara tuntas adalah Rp 950.000. Bagaimana analisis Anda?",
     "opts": [
         ("Mengajukan penggantian komponen satu set baru (Rp 950.000) dengan menyertakan hitungan bahwa servis tambal-sulam berulang justru merugikan perusahaan Rp 1.600.000 per bulan.", 5),
         ("Tetap melakukan servis tambal-sulam Rp 400.000 setiap minggu agar sekali pengajuan nominalnya terlihat lebih kecil.", 2),
         ("Membiarkan genset tersebut rusak tanpa diajukan perbaikannya sama sekali.", 1),
         ("Meminta teknisi membeli komponen murahan tanpa garansi yang tidak sesuai spesifikasi.", 1)
     ]},
    {"id": 99, "sec": 11, "q": "99. [Strategi di Masa Efisiensi Anggaran] Apabila manajemen sedang menerapkan program penghematan biaya operasional sebesar 15% di seluruh area, langkah cerdas apa yang Anda ambil sebagai Leader tanpa mengorbankan SLA?",
     "opts": [
         ("Memperketat akurasi diagnosa awal sebelum berangkat (mencegah salah bawa sparepart/bolak-balik), mengoptimalkan rute gabungan, dan menghapus biaya-biaya tidak produktif.", 5),
         ("Mengurangi jumlah kunjungan penanganan gangguan darurat sebesar 15% secara langsung.", 1),
         ("Meminta anggota tim menalangi biaya BBM menggunakan uang gaji pribadi mereka tanpa diganti.", 1),
         ("Menghentikan seluruh kegiatan pemeliharaan preventif selama satu bulan penuh.", 2)
     ]},
    {"id": 100, "sec": 11, "q": "100. [Visi Bisnis Team Leader] Secara keseluruhan, bagaimana seorang Team Leader yang unggul memandang tim dan wilayah kerjanya dalam kacamata bisnis perusahaan?",
     "opts": [
         ("Memandang wilayah kerjanya sebagai unit bisnis yang harus dijaga reputasinya: menghasilkan kualitas layanan tertinggi bagi klien, menjaga efisiensi biaya operasional, nol kecurangan, dan memastikan seluruh tim tumbuh produktif.", 5),
         ("Memandang posisinya hanya sebagai penyambung pesan dari Koordinator ke teknisi tanpa perlu memikirkan risiko biaya.", 2),
         ("Memandang keberhasilan tim semata-mata dari seberapa banyak dana operasional yang berhasil dicairkan.", 1),
         ("Fokus mengejar keuntungan pribadi di lapangan selama target minimal tercapai.", 0)
     ]}
]

# ==========================================
# STATE MANAGEMENT
# ==========================================
if "step" not in st.session_state:
    st.session_state.step = 0
if "nama" not in st.session_state:
    st.session_state.nama = ""
if "area" not in st.session_state:
    st.session_state.area = ""
if "all_answers" not in st.session_state:
    st.session_state.all_answers = {}  # Menyimpan {qid: (huruf_dipilih, teks_opsi, poin)}
if "sec_start_time" not in st.session_state:
    st.session_state.sec_start_time = {}
if "overtime_log" not in st.session_state:
    st.session_state.overtime_log = {}

st.title("📋 Assessment Seleksi Calon Team Leader (100 Soal)")

# ==========================================
# TAHAP 0: IDENTITAS KANDIDAT
# ==========================================
if st.session_state.step == 0:
    st.info(
        "### 📌 Petunjuk Pengerjaan Assessment (100 Soal - 11 Bagian)\n"
        "- Soal terbagi ke dalam **11 Bagian Berurutan** (Kepemimpinan, Teknis, Sudut Pandang, Problem Solving, Profesionalisme, Integritas, Etika & Penilaian Tim, Penalaran Kompleks, Kemitraan Eksternal, Matematika Power, serta Pola Pikir Dana & Bisnis).\n"
        "- **Posisi opsi jawaban (A, B, C, D) diacak secara otomatis oleh sistem** untuk setiap kandidat. Bacalah setiap pilihan dengan teliti dan serius.\n"
        "- Setiap bagian dilengkapi **Countdown Timer** sesuai tingkat kesulitan.\n"
        "- Pengerjaan hanya dilakukan **1x (satu kali)** dan hasil akhirnya langsung dikirim melalui tombol WhatsApp di halaman penutup."
    )
    with st.form("form_identitas"):
        col1, col2 = st.columns(2)
        with col1:
            inp_nama = st.text_input("Nama Lengkap Kandidat *", placeholder="Contoh: Fahmi / Adi Bowo Santoso")
        with col2:
            inp_area = st.text_input("Tim / Area Kerja *", placeholder="Contoh: KUT Palangkaraya")
        mulai_btn = st.form_submit_button("🚀 Mulai Kerjakan Bagian 1", use_container_width=True)
        
    if mulai_btn:
        if not inp_nama.strip() or not inp_area.strip():
            st.error("⚠️ Mohon lengkapi Nama Lengkap dan Area Kerja Anda terlebih dahulu!")
        else:
            st.session_state.nama = inp_nama.strip()
            st.session_state.area = inp_area.strip()
            st.session_state.step = 1
            st.session_state.sec_start_time[1] = time.time()
            st.rerun()

# ==========================================
# TAHAP 1 s/d 11: PENGERJAAN PER BAGIAN + TIMER
# ==========================================
elif 1 <= st.session_state.step <= 11:
    cur_sec = st.session_state.step
    sec_info = SECTIONS[cur_sec]
    if cur_sec not in st.session_state.sec_start_time:
        st.session_state.sec_start_time[cur_sec] = time.time()
        
    st.progress(cur_sec / 11.0, text=f"Progres Pengerjaan: Bagian {cur_sec} dari 11 ({int((cur_sec/11)*100)}%)")
    
    batas_detik = sec_info["minutes"] * 60
    waktu_berjalan = time.time() - st.session_state.sec_start_time[cur_sec]
    sisa_detik = max(0, int(batas_detik - waktu_berjalan))
    tampilkan_timer_visual(sisa_detik, cur_sec)
    
    st.subheader(sec_info["title"])
    st.caption(f"📌 {sec_info['desc']} | Alokasi Waktu: **{sec_info['minutes']} Menit**")
    st.divider()
    
    soal_bagian = [q for q in QUESTIONS if q["sec"] == cur_sec]
    
    with st.form(f"form_sec_{cur_sec}"):
        jawaban_sementara = {}
        peta_opsi_soal = {}
        
        for item in soal_bagian:
            qid = item["id"]
            st.markdown(f"**{item['q']}**")
            
            # Acak urutan opsi A, B, C, D secara deterministik per kandidat & nomor soal
            shuffled_dict = get_shuffled_options(st.session_state.nama, item)
            peta_opsi_soal[qid] = shuffled_dict
            
            opsi_tampil = [f"{huruf}. { shuffled_dict[huruf][0] }" for huruf in ["A", "B", "C", "D"]]
            dipilih = st.radio(
                f"Soal {qid}",
                options=opsi_tampil,
                index=None,
                key=f"q_{qid}",
                label_visibility="collapsed"
            )
            jawaban_sementara[qid] = dipilih
            st.write("")
            
        label_tombol = f"➡️ Simpan & Lanjut ke Bagian {cur_sec + 1}" if cur_sec < 11 else "✅ Selesai & Proses Hasil Assessment (100 Soal)"
        kirim_btn = st.form_submit_button(label_tombol, use_container_width=True)
        
    if kirim_btn:
        if None in jawaban_sementara.values():
            st.error(f"⚠️ Mohon jawab seluruh soal pada Bagian {cur_sec} ini sebelum melanjutkan!")
        else:
            durasi_aktual = time.time() - st.session_state.sec_start_time[cur_sec]
            lewat_waktu = durasi_aktual > (sec_info["minutes"] * 60 + 15)
            st.session_state.overtime_log[cur_sec] = {
                "durasi_menit": round(durasi_aktual / 60.0, 1),
                "batas_menit": sec_info["minutes"],
                "overtime": lewat_waktu
            }
            
            for qid, val_str in jawaban_sementara.items():
                huruf_pilih = val_str.split(".")[0]
                teks_opsi, poin_opsi = peta_opsi_soal[qid][huruf_pilih]
                st.session_state.all_answers[qid] = (huruf_pilih, teks_opsi, poin_opsi)
                
            st.session_state.step += 1
            if st.session_state.step <= 11:
                st.session_state.sec_start_time[st.session_state.step] = time.time()
            st.rerun()

# ==========================================
# TAHAP 12: SELESAI & KIRIM HASIL LENGKAP VIA WA
# ==========================================
elif st.session_state.step == 12:
    kat_scores = {i: 0 for i in range(1, 12)}
    skor_murni = 0
    kode_jawaban_ringkas = []
    
    for item in QUESTIONS:
        qid = item["id"]
        sec_id = item["sec"]
        huruf_pilih, _, poin = st.session_state.all_answers.get(qid, ("-", "", 0))
        kat_scores[sec_id] += poin
        skor_murni += poin
        kode_jawaban_ringkas.append(f"{qid}{huruf_pilih}:{poin}")
        
    penalti_waktu = 0
    info_waktu = []
    for s_idx in range(1, 12):
        log_w = st.session_state.overtime_log.get(s_idx, {})
        dur = log_w.get("durasi_menit", 0)
        if log_w.get("overtime", False):
            penalti_waktu += 2
            info_waktu.append(f"B{s_idx}:Telat({dur}m)")
        else:
            info_waktu.append(f"B{s_idx}:OK({dur}m)")
            
    total_skor_akhir = max(0, skor_murni - penalti_waktu)
    level_kandidat, remark_sifat = analisis_level_dan_sifat_100(total_skor_akhir, kat_scores, penalti_waktu)

    st.balloons()
    st.success("🎉 SELESAI! Seluruh 100 jawaban Anda telah berhasil diolah oleh sistem.")
    st.warning("Wajib: Klik tombol di bawah ini untuk mengirimkan hasil evaluasi Anda langsung ke WhatsApp Koordinator.")

    pesan_wa = (
        f"Halo Pak Okta, saya *{st.session_state.nama}* ({st.session_state.area}) telah menyelesaikan Assessment Calon Team Leader (100 Soal).\n\n"
        f"📊 *HASIL EVALUASI SISTEM:*\n"
        f"• Total Skor Akhir: *{total_skor_akhir} / 500* (Skor Murni: {skor_murni}, Penalti Waktu: -{penalti_waktu})\n"
        f"• Rekomendasi Level: *{level_kandidat}*\n\n"
        f"🧠 *ANALISIS KARAKTER & KECENDERUNGAN SIFAT:*\n{remark_sifat}\n\n"
        f"📈 *RINCIAN SKOR 11 BAGIAN:*\n"
        f"1. Kepemimpinan: {kat_scores[1]}/25\n"
        f"2. Teknis & Operasional: {kat_scores[2]}/25\n"
        f"3. Sudut Pandang: {kat_scores[3]}/25\n"
        f"4. Problem Solving: {kat_scores[4]}/25\n"
        f"5. Profesionalisme: {kat_scores[5]}/50\n"
        f"6. Integritas & Ketegasan: {kat_scores[6]}/25\n"
        f"7. Etika & Menilai Tim: {kat_scores[7]}/75\n"
        f"8. Penalaran Kompleks: {kat_scores[8]}/50\n"
        f"9. Kemitraan Eksternal: {kat_scores[9]}/75\n"
        f"10. Matematika Power: {kat_scores[10]}/75\n"
        f"11. Pola Pikir Dana & Bisnis: {kat_scores[11]}/50\n\n"
        f"⏱️ *Log Waktu:* {', '.join(info_waktu)}"
    )
    
    url_wa = f"https://wa.me/{NOMOR_WA_KOORDINATOR}?text={urllib.parse.quote(pesan_wa)}"
    st.link_button("📲 KLIK DI SINI UNTUK KIRIM HASIL KE WHATSAPP (08115251515)", url_wa, type="primary", use_container_width=True)
