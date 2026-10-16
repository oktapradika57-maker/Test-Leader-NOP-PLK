import streamlit as st
import streamlit.components.v1 as components
import urllib.parse
import time
import requests
from datetime import datetime

# ==========================================
# KONFIGURASI UTAMA & URL APPS SCRIPT ANDA
# ==========================================
SPREADSHEET_TITLE = "Request Operational NOP Palangkaraya (Jawaban)"
WORKSHEET_NAME = "Test Leader"
NOMOR_WA_KOORDINATOR = "628115251515"

# URL Google Apps Script Web App yang Anda berikan
APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxJpZKWC0XuD3NekvbQMefsx1JEZfOHx_5yubN5wU5O--6XTClW_5xlRlRGLdWqcLw/exec"

st.set_page_config(page_title="Assessment 60 Soal Calon Leader", page_icon="⏱️", layout="centered")

HEADERS_SHEET = [
    "Timestamp", "Nama Kandidat", "Tim / Area", 
    "Total Skor Akhir (Max 300)", "Skor Murni", "Penalti Waktu", "Catatan Ketepatan Waktu",
    "Status Kelulusan", "Remark Karakteristik Lengkap",
    "Bag 1: Kepemimpinan (25)", "Bag 2: Teknis (25)", 
    "Bag 3: Sudut Pandang (25)", "Bag 4: Problem Solving (25)",
    "Bag 5: Pribadi vs Prof (50)", "Bag 6: Integritas & Pemecatan (25)",
    "Bag 7: Etika Bos-Bawahan & Penilaian Tim (75)", "Bag 8: Penalaran Kompleks (50)"
] + [f"Soal {i}" for i in range(1, 61)]

def simpan_ke_spreadsheet(row_data):
    """Mengirim data langsung ke Spreadsheet via Google Apps Script (Anti-Gagal & Tanpa Secrets)."""
    if not APPS_SCRIPT_URL.strip().startswith("https://script.google.com"):
        raise ValueError("URL Apps Script belum diisi dengan benar.")
        
    payload = {
        "headers": HEADERS_SHEET,
        "row": row_data
    }
    
    response = requests.post(APPS_SCRIPT_URL.strip(), json=payload, timeout=20)
    if response.status_code == 200:
        return True
    else:
        raise Exception(f"Server Apps Script merespons error: {response.text}")

def buat_remark_karakter_60(kat, penalti_waktu):
    catatan = []
    if kat[1] >= 20:
        catatan.append("[Kepemimpinan]: Kuat, tegas & bertanggung jawab.")
    else:
        catatan.append("[Kepemimpinan]: Masih ragu/lemah mengatur anggota.")
        
    if kat[2] + kat[4] >= 40:
        catatan.append("[Teknis & Taktis]: Penguasaan prioritas lapangan & RCA sangat matang.")
    else:
        catatan.append("[Teknis & Taktis]: Perlu peningkatan dalam analisis teknis & prioritas gangguan.")
        
    if kat[5] >= 40:
        catatan.append("[Profesionalisme]: Dewasa memisahkan urusan pribadi dan pekerjaan.")
    else:
        catatan.append("[Profesionalisme]: Rawan membawa masalah/emosi pribadi ke pekerjaan.")
        
    if kat[6] >= 22:
        catatan.append("[Integritas]: TANPA KOMPROMI pada kecurangan & berani memecat anggota pembangkang.")
    else:
        catatan.append("[Integritas]: PERINGATAN! Masih kompromi pada pelanggaran atau tidak tega menindak pembangkang.")
        
    if kat[7] >= 62:
        catatan.append("[Relasi Bos-Bawahan & Penilaian Tim]: Sangat adil menilai KPI individu, hormat & solutif ke Bos, tegas & manusiawi ke bawahan.")
    else:
        catatan.append("[Relasi Bos-Bawahan & Penilaian Tim]: Cenderung subjektif menilai tim atau kurang tepat menjaga etika ke atasan/bawahan.")
        
    if kat[8] >= 40:
        catatan.append("[Penalaran Kompleks]: Logika analitis tajam dalam memecahkan masalah rumit.")
    else:
        catatan.append("[Penalaran Kompleks]: Penalaran logika & pemecahan masalah rumit masih lemah.")

    if penalti_waktu == 0:
        catatan.append("[Manajemen Waktu]: Disiplin tinggi, menyelesaikan seluruh bagian tepat waktu.")
    else:
        catatan.append(f"[Manajemen Waktu]: Terlambat di beberapa bagian (Penalti -{penalti_waktu} poin).")
        
    return " | ".join(catatan)

# ==========================================
# KOMPONEN VISUAL COUNTDOWN TIMER (JAVASCRIPT)
# ==========================================
def tampilkan_timer_visual(sisa_detik, nomor_bagian):
    timer_html = f"""
    <div style="background-color:#1e293b; color:#f8fafc; padding:12px 18px; border-radius:10px; 
                display:flex; justify-content:space-between; align-items:center; font-family:sans-serif; 
                border-left: 6px solid #3b82f6; margin-bottom:10px;">
        <div>
            <span style="font-size:14px; color:#94a3b8;">⏱️ Batas Waktu Pengerjaan Bagian {nomor_bagian}:</span><br>
            <strong style="font-size:15px;">Jawab dengan teliti sebelum waktu habis!</strong>
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
# KONFIGURASI 8 BAGIAN & TIMER SESUAI KESULITAN
# ==========================================
SECTIONS = {
    1: {"title": "Bagian 1: Kepemimpinan & Manajemen Tim", "desc": "5 Soal | Tingkat Kesulitan: Sedang", "minutes": 6},
    2: {"title": "Bagian 2: Teknis & Operasional Lapangan", "desc": "5 Soal | Tingkat Kesulitan: Tinggi (Teknis & Triage)", "minutes": 8},
    3: {"title": "Bagian 3: Sudut Pandang & Ownership Kerja", "desc": "5 Soal | Tingkat Kesulitan: Sedang", "minutes": 6},
    4: {"title": "Bagian 4: Pola Pikir & Penyelesaian Masalah Taktis", "desc": "5 Soal | Tingkat Kesulitan: Tinggi (Studi Kasus)", "minutes": 8},
    5: {"title": "Bagian 5: Kehidupan Pribadi vs Profesional", "desc": "10 Soal | Tingkat Kesulitan: Sedang - Tinggi", "minutes": 10},
    6: {"title": "Bagian 6: Integritas, Norma Komunikasi & Ketegasan Pemecatan", "desc": "5 Soal | Tingkat Kesulitan: Prinsipil & Ketegasan Mutlak", "minutes": 6},
    7: {"title": "Bagian 7: Etika Berperilaku (Dengan Bos, Bawahan, Sesama) & Menilai Individu Tim", "desc": "15 Soal | Tingkat Kesulitan: Komprehensif", "minutes": 15},
    8: {"title": "Bagian 8: Penalaran Logis & Penyelesaian Masalah Kompleks", "desc": "10 Soal | Tingkat Kesulitan: Sangat Tinggi (Logika & Analisis)", "minutes": 15}
}

# ==========================================
# DATABASE 60 SOAL TERSTRUKTUR PER BAGIAN
# ==========================================
QUESTIONS = [
    # ---------------- BAGIAN 1: KEPEMIMPINAN (Soal 1-5) ----------------
    {"id": 1, "sec": 1, "q": "1. Di tim Anda terdapat dua anggota: Anggota A cepat teknis tapi lemah administrasi, Anggota B rapi administrasi tapi lambat teknis. Saat ada pekerjaan mendesak, bagaimana Anda mengatur mereka?",
     "opts": {"A": ("Menugaskan Anggota A mengerjakan semuanya, meminta B buat laporan dari kantor.", 2),
              "B": ("Memasangkan keduanya: A fokus eksekusi teknis, B mendampingi memastikan kelengkapan data real-time sambil belajar.", 5),
              "C": ("Menurunkan tangan sendiri mengerjakan bagian terberat agar tidak pusing.", 3),
              "D": ("Menegur keras keduanya sebelum berangkat agar tidak mengulangi kelemahan.", 1)}},
    {"id": 2, "sec": 1, "q": "2. Anggota tim senior berkeahlian tinggi berulang kali terlambat melengkapi laporan dan meremehkan administrasi. Apa tindakan Anda?",
     "opts": {"A": ("Memakluminya selama teknis aman, lalu membantu melengkapi laporannya.", 2),
              "B": ("Memanggil empat mata, mengapresiasi skill-nya, namun menegaskan pekerjaan belum selesai (0%) jika laporan belum masuk, serta menetapkan konsekuensi.", 5),
              "C": ("Langsung melaporkannya ke Koordinator agar diberi SP tanpa diskusi.", 3),
              "D": ("Menyindirnya di grup WhatsApp tim agar dia merasa malu.", 1)}},
    {"id": 3, "sec": 1, "q": "3. Tim Anda gagal mencapai target SLA karena kesalahan salah satu anggota. Saat dievaluasi atasan, apa yang Anda sampaikan?",
     "opts": {"A": ("Menyebutkan nama anggota yang bersalah secara langsung agar atasan tahu bukan salah Anda.", 1),
              "B": ("Mengambil tanggung jawab penuh sebagai Leader, menjelaskan akar masalah secara objektif, dan memaparkan langkah pencegahan ke depan.", 5),
              "C": ("Menyalahkan faktor eksternal seperti cuaca atau peralatan kurang mendukung.", 2),
              "D": ("Meminta anggota tersebut menghadap atasan sendirian untuk menjelaskan kesalahannya.", 3)}},
    {"id": 4, "sec": 1, "q": "4. Tim harus menangani gangguan darurat malam hari saat cuaca buruk, sementara anggota mulai mengeluh kelelahan. Sikap Anda?",
     "opts": {"A": ("Memerintahkan tetap berangkat sambil dipantau lewat telepon tiap jam.", 3),
              "B": ("Hadir langsung memimpin/memastikan logistik & keamanan, memberi arahan tenang, serta mengatur rotasi istirahat.", 5),
              "C": ("Menunda pekerjaan sampai besok pagi tanpa koordinasi karena kasihan.", 2),
              "D": ("Mengancam memotong penilaian kinerja jika masih mengeluh.", 1)}},
    {"id": 5, "sec": 1, "q": "5. Anggota tim baru belum menguasai troubleshooting utama di tengah jadwal padat. Langkah yang Anda ambil?",
     "opts": {"A": ("Membiarkannya belajar sendiri melihat anggota lain bekerja.", 2),
              "B": ("Membuatkan panduan checklist SOP, memasangkannya dengan senior, dan mengevaluasi 15-20 menit seusai kerja.", 5),
              "C": ("Hanya memberinya tugas ringan terus-menerus agar tidak menghambat.", 1),
              "D": ("Meminta atasan menukar anggota tersebut dengan yang berpengalaman.", 3)}},

    # ---------------- BAGIAN 2: TEKNIS OPERASIONAL (Soal 6-10) ----------------
    {"id": 6, "sec": 2, "q": "6. Muncul 3 tiket bersamaan: (1) A: listrik padam baterai 90% sehat, (2) B: DC drop kritis genset gagal start, (3) C: PM rutin. Urutan prioritas yang tepat:",
     "opts": {"A": ("Lokasi C -> Lokasi A -> Lokasi B (menyelesaikan yang rutin dulu).", 1),
              "B": ("Lokasi B -> Lokasi A -> Lokasi C (amankan titik kritis dulu, pantau A, lalu jadwalkan PM).", 5),
              "C": ("Lokasi A -> Lokasi B -> Lokasi C (karena tiket A masuk lebih dulu).", 3),
              "D": ("Menunggu instruksi atasan tanpa menggerakkan tim.", 2)}},
    {"id": 7, "sec": 2, "q": "7. Genset gagal menyala otomatis saat listrik padam dan muncul alarm gagal crank. Langkah pemeriksaan teknis pertama yang sistematis:",
     "opts": {"A": ("Langsung membongkar mesin atau mengganti modul kontrol tanpa cek dasar.", 2),
              "B": ("Memeriksa parameter dasar berurutan: tegangan aki, BBM & jalur solenoid, tombol Emergency/Auto, lalu coba manual start.", 5),
              "C": ("Me-reset alarm berulang kali sampai aki habis dengan harapan menyala sendiri.", 1),
              "D": ("Langsung menyimpulkan genset rusak berat dan meninggalkan lokasi.", 3)}},
    {"id": 8, "sec": 2, "q": "8. Anggota mengirim laporan PM dengan waktu sangat cepat, namun angka & foto dokumentasi sangat mirip bulan lalu. Tindakan Anda?",
     "opts": {"A": ("Langsung menyetujui agar target kuantitas harian tercapai.", 1),
              "B": ("Menahan laporan, memeriksa metadata foto & histori parameter, serta mewajibkan pengukuran ulang valid via video call/kunjungan.", 5),
              "C": ("Mengubah sendiri angka di laporan agar sedikit berbeda.", 2),
              "D": ("Menghapus laporan tersebut tanpa memberitahu anggota.", 3)}},
    {"id": 9, "sec": 2, "q": "9. Sebelum tim berangkat penanganan gangguan berjarak 3 jam, prosedur kesiapan teknis apa yang wajib dipastikan Leader?",
     "opts": {"A": ("Cukup pastikan mobil isi bensin dan membawa tas kerja masing-masing.", 3),
              "B": ("Memeriksa alat ukur berfungsi, kelengkapan tools, sparepart sesuai gejala, serta kesiapan APD/K3.", 5),
              "C": ("Meminta tim langsung berangkat tanpa cek alat agar terlihat responsif.", 2),
              "D": ("Menyerahkan sepenuhnya ke teknisi tanpa verifikasi.", 1)}},
    {"id": 10, "sec": 2, "q": "10. Sisa 15 menit sebelum SLA habis, anggota meminta izin melompati prosedur K3 demi mempercepat pekerjaan. Keputusan Anda?",
     "opts": {"A": ("Mengizinkan khusus kali ini yang penting SLA tidak lewat.", 2),
              "B": ("Menolak tegas, wajib jalankan K3, sambil laporkan kondisi riil ke Koordinator bahwa keselamatan adalah prioritas.", 5),
              "C": ("Menyuruh teknisi melakukannya diam-diam asal tak terekam foto.", 1),
              "D": ("Menghentikan seluruh pekerjaan dan menyuruh tim pulang.", 3)}},

    # ---------------- BAGIAN 3: SUDUT PANDANG (Soal 11-15) ----------------
    {"id": 11, "sec": 3, "q": "11. Manajemen mewajibkan update laporan lengkap di sistem sebelum pencairan dana operasional berikutnya. Anggota mengeluh menghambat. Sikap Anda?",
     "opts": {"A": ("Ikut mengeluh dan menyalahkan aturan manajemen.", 1),
              "B": ("Memahami pentingnya akuntabilitas data, mendisiplinkan tim agar langsung submit laporan begitu pekerjaan selesai sehingga dana tidak terkunci.", 5),
              "C": ("Mencari celah menginput data kosong/palsu asal dana cair.", 2),
              "D": ("Membiarkan anggota protes ke admin tanpa memberikan solusi.", 3)}},
    {"id": 12, "sec": 3, "q": "12. Saat di lokasi menyelesaikan tiket ringan, Anda melihat anomali kabel panas pada perangkat lain yang belum ada tiket tapi berpotensi down. Tindakan Anda?",
     "opts": {"A": ("Mengabaikannya karena bukan ruang lingkup tiket hari ini.", 2),
              "B": ("Melakukan tindakan pencegahan aman saat itu, dokumentasikan foto & data, dan laporkan sebagai preventive maintenance.", 5),
              "C": ("Menunggu sampai perangkat benar-benar rusak dan memunculkan tiket baru.", 1),
              "D": ("Hanya memfotonya dan disimpan di HP pribadi.", 3)}},
    {"id": 13, "sec": 3, "q": "13. Atasan menegur karena data laporan tim Anda banyak salah ketik dibanding area lain. Cara Anda menyikapinya?",
     "opts": {"A": ("Merasa tersinggung karena tim sudah bekerja keras secara fisik.", 2),
              "B": ("Menerima koreksi, mengecek kesalahan input, dan menerapkan verifikasi silang (double-check) sebelum data dikirim.", 5),
              "C": ("Berdebat bahwa akurasi data tidak penting selama perangkat menyala.", 1),
              "D": ("Memarahi admin atau anggota di depan umum untuk melampiaskan kesal.", 3)}},
    {"id": 14, "sec": 3, "q": "14. Terdapat sisa material/dana operasional setelah perbaikan, dan anggota mengusulkan tidak usah dilaporkan untuk uang makan. Sikap Anda?",
     "opts": {"A": ("Menyetujuinya selama jumlahnya kecil.", 1),
              "B": ("Menolak tegas, menegaskan integritas adalah harga mati, dan melaporkan seluruh sisa secara transparan.", 5),
              "C": ("Pura-pura tidak tahu dan menyerahkan pada anggota.", 2),
              "D": ("Mengambil sisa tersebut untuk disimpan sendiri.", 1)}},
    {"id": 15, "sec": 3, "q": "15. Terjadi selisih data rekap lapangan dengan catatan Admin Operasional. Sudut pandang Anda dalam menyelesaikannya?",
     "opts": {"A": ("Menganggap admin tidak becus dan menyerang admin di grup.", 1),
              "B": ("Memandang admin sebagai mitra, melakukan rekonsiliasi baik-baik menyandingkan bukti lapangan (log, foto, jam check-in).", 5),
              "C": ("Mengabaikan rekap admin karena merasa catatan lapangan pasti benar.", 2),
              "D": ("Meminta atasan menegur admin tanpa mengecek data tim sendiri.", 3)}},

    # ---------------- BAGIAN 4: POLA PIKIR & PROBLEM SOLVING (Soal 16-20) ----------------
    {"id": 16, "sec": 4, "q": "16. Lokasi mengalami gangguan berulang 3x sebulan dengan gejala sama, teknisi selama ini hanya mereset dan normal sementara. Pola pikir Anda:",
     "opts": {"A": ("Tetap lakukan reset tiap gangguan muncul karena paling cepat.", 2),
              "B": ("Hentikan pola tambal sulam; lakukan Root Cause Analysis (analisis tren beban, tegangan, suhu) untuk solusi permanen.", 5),
              "C": ("Menyalahkan kualitas perangkat tua tanpa pengukuran data.", 3),
              "D": ("Meminta lokasi tersebut dipindah ke tim lain.", 1)}},
    {"id": 17, "sec": 4, "q": "17. Di tengah perjalanan ke gangguan kritis, kendaraan mogok dan sparepart kurang satu komponen. Cara Anda menyelesaikan masalah ganda ini:",
     "opts": {"A": ("Membatalkan perjalanan dan kembali ke kantor menunggu besok.", 2),
              "B": ("Membagi fokus taktis: satu orang urus kendaraan/transport alternatif, Anda berkoordinasi dengan rekan/toko teknik untuk komponen serta update estimasi waktu ke Koordinator.", 5),
              "C": ("Panik dan mematikan komunikasi karena takut dimarahi.", 1),
              "D": ("Memaksakan kendaraan rusak parah jalan terus membahayakan nyawa.", 3)}},
    {"id": 18, "sec": 4, "q": "18. Anda diberi akses histori data daya, baterai, dan gangguan 3 bulan. Bagaimana Anda memanfaatkannya?",
     "opts": {"A": ("Hanya disimpan sebagai arsip jika ditanya saat audit.", 3),
              "B": ("Memetakan lokasi penurunan performa tajam untuk dijadikan prioritas jadwal kunjungan pencegahan sebelum down.", 5),
              "C": ("Bingung membacanya dan menyerahkan seluruh analisis ke atasan.", 2),
              "D": ("Hanya melihat lokasi yang kondisinya bagus untuk dilaporkan.", 1)}},
    {"id": 19, "sec": 4, "q": "19. Dua anggota berdebat keras soal letak kerusakan hingga pekerjaan terhenti. Cara Anda mengurai masalah:",
     "opts": {"A": ("Membiarkan berdebat sampai salah satu mengalah sendiri.", 2),
              "B": ("Menengahi kepala dingin, hentikan asumsi, arahkan pembuktian berbasis pengukuran alat ukur satu persatu secara objektif.", 5),
              "C": ("Membela anggota yang lebih dekat secara pribadi tanpa cek perangkat.", 1),
              "D": ("Memulangkan keduanya dan dikerjakan sendiri.", 3)}},
    {"id": 20, "sec": 4, "q": "20. Rencana kerja mingguan harus berubah di hari Rabu karena ada instruksi audit mendadak di beberapa titik. Cara Anda beradaptasi:",
     "opts": {"A": ("Menolak instruksi baru karena jadwal mingguan tidak boleh diubah.", 1),
              "B": ("Re-planning cepat: gabungkan rute searah target rutin dan mendadak, atur ulang skala prioritas, dan komunikasikan ke atasan.", 5),
              "C": ("Menghentikan seluruh pekerjaan rutin seminggu penuh.", 2),
              "D": ("Bekerja acak tanpa perencanaan karena merasa menyusun jadwal sia-sia.", 3)}},

    # ---------------- BAGIAN 5: KEHIDUPAN PRIBADI & PROFESIONAL (Soal 21-30) ----------------
    {"id": 21, "sec": 5, "q": "21. Anggota tim sering menghubungi Anda tengah malam untuk curhat non-darurat. Batasan komunikasi profesional yang Anda terapkan?",
     "opts": {"A": ("Memarahi dan memblokir nomor anggota agar tidak mengganggu istirahat.", 1),
              "B": ("Menetapkan norma komunikasi: siap tanggap untuk darurat operasional, namun mengarahkan hal non-darurat dibahas pada jam kerja esok hari.", 5),
              "C": ("Selalu melayani obrolan pribadi mereka sampai larut malam setiap hari.", 2),
              "D": ("Mengabaikan semua panggilan selamanya termasuk panggilan darurat lapangan.", 1)}},
    {"id": 22, "sec": 5, "q": "22. Performa anggota tim menurun drastis karena masalah keluarga/finansial berat di rumah. Sikap Anda sebagai leader:",
     "opts": {"A": ("Memecatnya langsung karena dianggap tidak profesional.", 1),
              "B": ("Memanggil empat mata dengan empati, mendengarkan kondisinya, memberikan dukungan/penyesuaian tugas sementara, namun tetap menjaga target kerja.", 5),
              "C": ("Membiarkan dan memotong gajinya tiap kali hasil kerja jelek.", 2),
              "D": ("Ikut mencampuri dan menggosipkan masalah pribadinya ke tim lain.", 1)}},
    {"id": 23, "sec": 5, "q": "23. Menjelang akhir pekan saat libur bersama keluarga, ada laporan minor dari lapangan yang bisa ditangani teknisi piket. Keputusan Anda?",
     "opts": {"A": ("Meninggalkan keluarga dan turun tangan sendiri ke lapangan.", 2),
              "B": ("Mempercayakan ke teknisi piket, pantau secara jarak jauh via sistem, biarkan sistem berjalan dan tetap siaga jika ada eskalasi.", 5),
              "C": ("Mematikan HP dan pura-pura tidak tahu ada masalah.", 1),
              "D": ("Memarahi teknisi piket karena berani menelepon di hari libur.", 1)}},
    {"id": 24, "sec": 5, "q": "24. Salah satu anggota tim adalah teman dekat/kerabat Anda di luar kantor. Bagaimana cara Anda memperlakukan kinerjanya?",
     "opts": {"A": ("Memberikan dispensasi khusus, memaklumi keterlambatan dan meringankan laporan.", 1),
              "B": ("Tetap objektif dan profesional: memberlakukan standar aturan, teguran, dan penilaian yang persis sama tanpa keistimewaan.", 5),
              "C": ("Menjaganya agar tidak disentuh pekerjaan berat agar pertemanan tidak rusak.", 2),
              "D": ("Justru memberi beban paling berat untuk membuktikan tidak pilih kasih.", 3)}},
    {"id": 25, "sec": 5, "q": "25. Anda sedang stres berat akibat tekanan atasan, lalu anggota tim membuat kesalahan sepele di lapangan. Cara Anda mengendalikan emosi:",
     "opts": {"A": ("Melampiaskan kemarahan dari atasan kepada anggota tim tersebut.", 1),
              "B": ("Memisahkan emosi: tenangkan diri, tegur kesalahan secara objektif terfokus pada perbaikan, susun strategi lapor atasan tanpa amarah.", 5),
              "C": ("Diam memendam stres sampai jatuh sakit.", 2),
              "D": ("Mengancam resign di depan tim karena tidak tahan tekanan.", 1)}},
    {"id": 26, "sec": 5, "q": "26. Anggota tim sering menyindir manajemen atau menyebar info internal di status media sosial pribadinya. Tindakan Anda:",
     "opts": {"A": ("Ikut menyukai atau mengomentari postingan tersebut.", 1),
              "B": ("Menegur pribadi, jelaskan dampak pelanggaran kerahasiaan & etika profesional, minta postingan dihapus demi nama baik tim.", 5),
              "C": ("Membalas menyindir secara terbuka di media sosial.", 1),
              "D": ("Pura-pura tidak melihat karena medsos adalah hak pribadi.", 2)}},
    {"id": 27, "sec": 5, "q": "27. Terjadi down total di wilayah kerja saat Anda harus menghadiri acara keluarga penting. Sikap Anda:",
     "opts": {"A": ("Mengabaikan kantor dan tetap di acara keluarga sepenuhnya.", 1),
              "B": ("Mengomunikasikan situasi ke keluarga, turun tangan/koordinasi darurat jarak jauh hingga sistem pulih, lalu atur waktu keluarga setelahnya.", 5),
              "C": ("Memarahi keluarga karena mengadakan acara di saat jadwal kerja berantakan.", 1),
              "D": ("Meminta anggota selesaikan sendiri, Anda acuh tak acuh.", 2)}},
    {"id": 28, "sec": 5, "q": "28. Mulai terbentuk kubu-kubuan di dalam tim yang saling tidak akur. Cara Anda mengatasinya:",
     "opts": {"A": ("Memihak salah satu kubu yang lebih sering membantu Anda.", 1),
              "B": ("Mengadakan pertemuan, tegaskan tim hanya satu kesatuan, fokus pada target bersama, tindak tegas perilaku toksik.", 5),
              "C": ("Membiarkan bersaing tidak sehat karena mengira memotivasi.", 2),
              "D": ("Ikut membicarakan keburukan kubu sebelah.", 1)}},
    {"id": 29, "sec": 5, "q": "29. Beredar gosip di tim bahwa tunjangan/libur akan dipotong manajemen pusat sehingga tim resah. Tindakan Anda:",
     "opts": {"A": ("Ikut memanaskan situasi dan menyebarkan gosip.", 1),
              "B": ("Meredam keresahan, konfirmasi fakta valid ke atasan/admin, sampaikan penjelasan transparan menenangkan berdasarkan data resmi.", 5),
              "C": ("Mendiamkan sampai tim melakukan mogok kerja.", 1),
              "D": ("Mengancam memecat siapa saja yang membicarakan gosip.", 2)}},
    {"id": 30, "sec": 5, "q": "30. Evaluasi diri (Self-Leadership) apa yang rutin Anda lakukan setiap akhir bulan?",
     "opts": {"A": ("Merasa diri paling benar karena tidak pernah ditegur atasan.", 1),
              "B": ("Refleksi objektif: review pencapaian, evaluasi kekurangan kepemimpinan diri, aktif minta masukan Koordinator/Admin untuk perbaikan.", 5),
              "C": ("Menyalahkan seluruh kegagalan murni kebodohan anggota lapangan.", 2),
              "D": ("Menunggu ada yang memuji baru merasa puas.", 1)}},

    # ---------------- BAGIAN 6: INTEGRITAS & PEMECATAN (Soal 31-35) ----------------
    {"id": 31, "sec": 6, "q": "31. Anda menemukan teknisi berkeahlian tinggi melakukan pemalsuan data KM dan manipulasi nota BBM untuk keuntungan pribadi. Tindakan tegas Anda:",
     "opts": {"A": ("Memakluminya karena tenaganya masih sangat dibutuhkan di lapangan.", 1),
              "B": ("Tegakkan integritas tanpa kompromi: proses sanksi berat / rekomendasi pemecatan karena kejujuran mutlak di atas keahlian.", 5),
              "C": ("Hanya tegur lisan asal berjanji tidak mengulangi tanpa sanksi tertulis.", 2),
              "D": ("Meminta bagian uang hasil manipulasi agar Anda tutup mulut.", 0)}},
    {"id": 32, "sec": 6, "q": "32. Anggota tim secara terbuka menolak instruksi kerja resmi, menantang otoritas Anda, dan membangkang. Langkah tegas Anda:",
     "opts": {"A": ("Menangis atau diam saja karena takut dimusuhi.", 1),
              "B": ("Tegur keras tertutup, catat pembangkangan tertulis, laporkan ke Koordinator, dan proses rekomendasi pemecatan jika tidak berubah demi wibawa tim.", 5),
              "C": ("Membiarkan membangkang asal perangkat lapangan menyala.", 2),
              "D": ("Membalas membentak dan memukul meja berisiko kekerasan fisik.", 1)}},
    {"id": 33, "sec": 6, "q": "33. Anggota tim sering menggunakan bahasa kasar, merendahkan rekan lain, atau menantang di grup WhatsApp resmi. Tindakan Anda:",
     "opts": {"A": ("Ikut tertawa dan membiarkan agar suasana grup santai.", 1),
              "B": ("Tegur tegas di grup bahwa ada norma kesopanan & etika profesional, bina empat mata, beri SP jika diulangi.", 5),
              "C": ("Keluar dari grup WhatsApp karena tidak tahan.", 2),
              "D": ("Memblokir anggota tanpa peringatan atau penjelasan.", 1)}},
    {"id": 34, "sec": 6, "q": "34. Pihak vendor memberikan sejumlah uang/fasilitas khusus agar laporan audit dipercepat atau anomali ditutup-tutupi. Sikap Anda:",
     "opts": {"A": ("Menerima dan membagikannya diam-diam ke tim.", 0),
              "B": ("Tolak tegas, edukasi tim bahwa suap/pungli mencoreng perusahaan dan berujung pemecatan seketika, laporkan ke manajemen.", 5),
              "C": ("Pura-pura tidak tahu asal Anda tidak ikut tanda tangan.", 1),
              "D": ("Memarahi pemberi suap dengan nada kasar di depan umum.", 2)}},
    {"id": 35, "sec": 6, "q": "35. Anggota sudah 3 kali diberi SP terkait pembangkangan, manipulasi data, dan pelanggaran etika komunikasi yang merusak tim. Keputusan akhir Anda:",
     "opts": {"A": ("Terus memberi kesempatan ke-4 dan ke-5 karena kasihan.", 1),
              "B": ("Ajukan rekomendasi pemecatan terstruktur ke manajemen melampirkan rekam jejak objektif, karena individu toksik & pembangkang harus dibersihkan.", 5),
              "C": ("Mengeluarkan dari grup WhatsApp kantor saja tanpa lapor HR/Koordinator.", 2),
              "D": ("Menurunkan gajinya secara sepihak tanpa prosedur resmi.", 1)}},

    # ---------------- BAGIAN 7 [BARU]: ETIKA BOS-BAWAHAN-MANUSIA & MENILAI TIM (Soal 36-50) ----------------
    {"id": 36, "sec": 7, "q": "36. [Etika ke Atasan] Bos/Koordinator menetapkan target baru yang menurut pengamatan Anda sangat sulit dicapai dengan kondisi peralatan saat ini. Bagaimana cara Anda merespons Bos?",
     "opts": {"A": ("Langsung menolak di depan umum dan mengatakan bahwa Bos tidak mengerti kondisi lapangan.", 1),
              "B": ("Menerima arahan dengan sikap hormat, lalu berdiskusi secara empat mata menyajikan data riil lapangan serta mengajukan opsi solusi/kebutuhan dukungan agar target tersebut bisa tercapai.", 5),
              "C": ("Mengiyakan saja di depan Bos asal Bos senang, tapi di belakang menyuruh tim tidak usah dikerjakan.", 1),
              "D": ("Mengeluh di belakang Bos kepada anggota tim bahwa Bos terlalu menuntut.", 2)}},
    {"id": 37, "sec": 7, "q": "37. [Etika ke Atasan] Saat terjadi masalah besar di lapangan, bagaimana cara terbaik seorang Leader melapor kepada Bos/Koordinator?",
     "opts": {"A": ("Hanya melempar masalah mentah-mentah ('Pak, lokasi A mati, gimana ini?') tanpa melakukan pengecekan apapun.", 2),
              "B": ("Melapor dengan prinsip Solutif: menyampaikan fakta kejadian secara ringkas, penyebab awal yang sudah diperiksa, dan membawa minimal 2 opsi rencana tindakan untuk diputuskan bersama Bos.", 5),
              "C": ("Menyembunyikan masalah tersebut sampai Bos tahu sendiri dari komplain pusat.", 1),
              "D": ("Menunggu ditanya Bos baru memberikan laporan.", 2)}},
    {"id": 38, "sec": 7, "q": "38. [Etika ke Atasan] Bos memberikan teguran keras kepada Anda di grup karena keterlambatan progres tim. Bagaimana sikap dan balasan Anda?",
     "opts": {"A": ("Membalas dengan kalimat defensif panjang lebar dan menyalahkan anggota tim di grup tersebut.", 1),
              "B": ("Menerima teguran dengan lapang dada tanpa berdebat kusir, meminta maaf secara profesional, dan segera mengirimkan rencana aksi perbaikan beserta batas waktu penyelesaiannya.", 5),
              "C": ("Mendiamkan pesan Bos (hanya dibaca) karena merasa kesal.", 1),
              "D": ("Meminta anggota tim yang menjawab teguran Bos tersebut.", 2)}},
    {"id": 39, "sec": 7, "q": "39. [Loyalitas & Penjembatan] Anggota tim memprotes kebijakan baru dari Bos/Koordinator. Bagaimana posisi Anda di tengah-tengah antara Bos dan Bawahan?",
     "opts": {"A": ("Ikut memanas-manasi bawahan agar membenci Bos supaya Anda terlihat kompak dengan bawahan.", 1),
              "B": ("Menjadi jembatan yang loyal dan bijak: menjelaskan tujuan positif kebijakan Bos kepada bawahan dengan bahasa yang mudah diterima, sekaligus menampung kendala teknis bawahan untuk disampaikan secara sopan ke Bos.", 5),
              "C": ("Menakut-nakuti bawahan dengan membawa-bawa nama Bos secara arogan.", 2),
              "D": ("Cuci tangan dan mengatakan 'Saya cuma disuruh Bos, jangan protes ke saya'.", 2)}},
    {"id": 40, "sec": 7, "q": "40. [Etika ke Bawahan] Bagaimana prinsip utama Anda dalam memperlakukan bawahan saat memberikan teguran maupun apresiasi?",
     "opts": {"A": ("Mempermalukan bawahan di depan umum saat salah, dan diam saja saat mereka berhasil.", 1),
              "B": ("Memuji dan mengapresiasi keberhasilan di depan tim untuk membangun semangat, serta menegur atau mengoreksi kesalahan secara empat mata dengan tegas namun tetap menjaga harga dirinya.", 5),
              "C": ("Tidak pernah menegur sama sekali karena takut bawahan tersinggung.", 2),
              "D": ("Mengakui hasil kerja keras bawahan di lapangan sebagai hasil kerja Anda sendiri di depan Bos.", 0)}},
    {"id": 41, "sec": 7, "q": "41. [Etika ke Bawahan] Seorang bawahan mengajukan ide cara kerja baru yang ternyata lebih efisien daripada cara yang biasa Anda gunakan. Sikap Anda?",
     "opts": {"A": ("Menolak idenya karena gengsi merasa Anda adalah Leader yang harus lebih pintar.", 1),
              "B": ("Mendengarkan dengan terbuka, menguji kelayakannya, mengadopsi ide tersebut untuk tim, dan menyebutkan nama bawahan tersebut kepada Bos sebagai pemberi ide.", 5),
              "C": ("Mengambil idenya diam-diam lalu melaporkannya ke Bos seolah-olah itu murni ide Anda.", 1),
              "D": ("Membiarkan dia memakainya sendiri tanpa membagikannya ke anggota lain.", 2)}},
    {"id": 42, "sec": 7, "q": "42. [Etika Memanusiakan Manusia] Saat berinteraksi dengan warga lokal, penjaga lokasi (security/owner lahan), atau petugas kebersihan di lapangan, bagaimana sikap yang wajib Anda contohkan ke tim?",
     "opts": {"A": ("Bersikap angkuh dan memerintah karena merasa kita adalah tim teknis yang lebih penting.", 1),
              "B": ("Menghormati setiap orang tanpa memandang status sosial, menyapa dengan sopan, dan menjaga hubungan baik karena kelancaran akses lokasi sangat bergantung pada respek antarmanusia.", 5),
              "C": ("Acuh tak acuh, langsung masuk lokasi tanpa izin atau tegur sapa.", 2),
              "D": ("Hanya bersikap sopan kepada pejabat atau atasan saja.", 1)}},
    {"id": 43, "sec": 7, "q": "43. [Etika Antar-Tim] Tim dari cluster/area tetangga sedang mengalami gangguan berat beruntun dan meminta bantuan teknis/informasi kepada tim Anda, padahal pekerjaan di area Anda sudah selesai. Sikap Anda?",
     "opts": {"A": ("Menolak membantu karena merasa bukan urusan area Anda dan takut direpotkan.", 1),
              "B": ("Selama area sendiri sudah aman dan mendapat izin Koordinator, siap memberikan bantuan teknis atau berbagi solusi karena keberhasilan perusahaan adalah keberhasilan bersama.", 5),
              "C": ("Menertawakan kesulitan tim area lain agar tim Anda terlihat paling hebat di mata Bos.", 0),
              "D": ("Membantu tapi dengan syarat meminta imbalan uang pribadi dari leader area sebelah.", 1)}},
    {"id": 44, "sec": 7, "q": "44. [Cara Menilai Individu Tim] Dalam memberikan nilai evaluasi bulanan kepada setiap anggota tim, parameter apa yang Anda jadikan dasar utama?",
     "opts": {"A": ("Kedekatan pribadi, siapa yang paling sering menemani ngopi atau paling pandai menyenangkan hati Anda.", 1),
              "B": ("Gabungan objektif berbasis data: Kecepatan & kualitas teknis (SLA), ketertiban submit laporan/data, kedisiplinan sikap/absensi, serta integritas kejujuran.", 5),
              "C": ("Memberikan nilai rata-rata yang sama persis untuk semua orang agar tidak pusing berpikir.", 2),
              "D": ("Hanya menilai berdasarkan faktor senioritas (lama bekerja) saja.", 2)}},
    {"id": 45, "sec": 7, "q": "45. [Cara Menilai Individu Tim] Anggota X jarang banyak bicara di grup namun setiap ditugaskan ke lokasi selalu tuntas, rapi datanya, dan zero komplain. Anggota Y sangat aktif bicara di grup namun pekerjaannya sering tidak tuntas. Bagaimana penilaian Anda?",
     "opts": {"A": ("Memberi nilai lebih tinggi kepada Anggota Y karena terlihat lebih ramai dan aktif di grup.", 1),
              "B": ("Memberikan nilai tinggi secara adil kepada Anggota X berdasarkan bukti hasil kerja nyata (output & kualitas), sambil membina Anggota Y agar menyeimbangkan komunikasi dengan kualitas eksekusi.", 5),
              "C": ("Menilai keduanya buruk karena masing-masing punya kekurangan.", 2),
              "D": ("Menilai berdasarkan siapa yang terakhir kali berbuat salah kemarin.", 1)}},
    {"id": 46, "sec": 7, "q": "46. [Cara Menilai Individu Tim] Seorang anggota tim sudah bekerja keras seharian di lapangan, namun pekerjaan tetap belum selesai tepat waktu karena faktor bencana alam (banjir/jalan putus) yang terbuktikan dengan dokumentasi valid. Bagaimana Anda menilai kinerjanya?",
     "opts": {"A": ("Tetap memberi nilai nol dan memarahinya karena hanya melihat hasil akhir tanpa peduli kendala.", 1),
              "B": ("Menilai secara adil dan proporsional: tetap mengapresiasi usaha dan kepatuhan pelaporan real-time-nya di lapangan, serta mencatat faktor kahar (force majeure) secara objektif di laporan evaluasi.", 5),
              "C": ("Menyuruhnya memalsukan jam selesai pekerjaan agar terlihat tidak terlambat.", 1),
              "D": ("Langsung menggantinya dengan orang lain keesokan harinya.", 2)}},
    {"id": 47, "sec": 7, "q": "47. [Cara Menilai Individu Tim] Bagaimana cara Anda menghindari bias penilaian 'Effect Baru' (hanya menilai anggota dari kejadian 2 hari terakhir dan melupakan kinerjanya selama 3 minggu sebelumnya)?",
     "opts": {"A": ("Mengandalkan ingatan kepala saja saat akhir bulan.", 2),
              "B": ("Memiliki catatan log mingguan sederhana (rekap tiket selesai, ketepatan laporan, dan catatan sikap) sehingga penilaian akhir bulan murni akumulasi fakta selama 30 hari penuh.", 5),
              "C": ("Bertanya kepada anggota lain siapa yang menurut mereka pantas dapat nilai bagus.", 2),
              "D": ("Menebak-nebak nilai secara acak.", 1)}},
    {"id": 48, "sec": 7, "q": "48. [Transparansi Penilaian] Saat Anda menyampaikan hasil penilaian kinerja yang kurang memuaskan kepada seorang bawahan, bawahan tersebut protes dan merasa tidak adil. Apa yang Anda lakukan?",
     "opts": {"A": ("Membentaknya dan mengatakan 'Keputusan Leader tidak bisa diganggu gugat!'.", 1),
              "B": ("Membuka data catatan kinerjanya secara transparan (jumlah keterlambatan laporan, histori komplain, dll.), menjelaskan letak kekurangannya secara spesifik, dan menyepakati target perbaikan untuk bulan depan.", 5),
              "C": ("Langsung mengubah nilainya menjadi bagus karena takut berdebat.", 1),
              "D": ("Menyalahkan Koordinator dengan berkata bahwa nilai itu kemauan Bos.", 1)}},
    {"id": 49, "sec": 7, "q": "49. [Keadilan Distribusi Beban] Saat membagi jadwal kunjungan lokasi yang jauh/sulit dan lokasi yang dekat/mudah, bagaimana cara Anda mengatur anggota tim?",
     "opts": {"A": ("Memberikan lokasi dekat terus-menerus kepada anggota favorit Anda, dan lokasi jauh terus-menerus ke anggota yang tidak Anda sukai.", 1),
              "B": ("Mengatur rotasi dan distribusi beban kerja secara adil dan proporsional sesuai kompetensi, serta mencatat histori penugasan agar tidak ada anggota yang merasa dianakemas atau dianaktirikan.", 5),
              "C": ("Membiarkan anggota berebut sendiri lokasi mana yang mereka mau.", 2),
              "D": ("Melempar undian koin setiap pagi tanpa melihat urgensi teknis.", 1)}},
    {"id": 50, "sec": 7, "q": "50. [Pengakuan Kontribusi Individu] Ketika tim Anda mendapatkan pujian dari Koordinator atas keberhasilan menyelesaikan proyek audit tepat waktu, bagaimana Anda bersikap?",
     "opts": {"A": ("Menerima pujian itu untuk diri sendiri tanpa menyebut peran anggota tim.", 1),
              "B": ("Mengucapkan terima kasih kepada Koordinator, lalu secara spesifik menyebutkan kontribusi nyata masing-masing anggota tim dan meneruskan apresiasi tersebut ke grup tim.", 5),
              "C": ("Meminta Koordinator langsung memberikan bonus uang saat itu juga.", 2),
              "D": ("Mengatakan bahwa pekerjaan itu sebenarnya sangat mudah.", 2)}},

    # ---------------- BAGIAN 8 [BARU]: PENALARAN LOGIS & PROBLEM SOLVING KOMPLEKS (Soal 51-60) ----------------
    {"id": 51, "sec": 8, "q": "51. [Penalaran Logis Sistematis] Sesuai aturan sistem: 'Jika teknisi belum submit laporan SIDATA, maka pengajuan dana SIRAPI otomatis terkunci'. Hari ini Teknisi Andi mengeluh tidak bisa mengajukan dana troubleshooting di SIRAPI, padahal ia merasa jaringan internetnya lancar. Kesimpulan logis pertama yang harus Anda periksa adalah:",
     "opts": {"A": ("Menyimpulkan aplikasi SIRAPI sedang rusak total untuk seluruh Kalimantan.", 1),
              "B": ("Memeriksa status kelengkapan submit laporan pekerjaan sebelumnya milik Teknisi Andi di sistem SIDATA, karena syarat pembuka kunci pengajuan dana adalah selesainya laporan sebelumnya.", 5),
              "C": ("Menyuruh Teknisi Andi membeli HP baru.", 1),
              "D": ("Meminta Admin mentransfer uang secara manual di luar sistem.", 2)}},
    {"id": 52, "sec": 8, "q": "52. [Penalaran Rute & Efisiensi] Ada 3 titik gangguan di jalur yang sama dari Kantor: Titik X (jarak 20 km, baterai tahan 6 jam), Titik Y (jarak 45 km, baterai kritis sisa 45 menit), dan Titik Z (jarak 50 km, jadwal PM rutin). Anda hanya punya 1 tim mobil dengan kecepatan rata-rata 60 km/jam. Strategi paling logis adalah:",
     "opts": {"A": ("Berhenti lama di Titik X dulu karena paling dekat, baru lanjut ke Titik Y.", 1),
              "B": ("Langsung melaju ke Titik Y (45 menit perjalanan) untuk menyelamatkan lokasi sebelum baterai habis, lanjut sekalian ke Titik Z yang hanya berjarak 5 km dari Y, lalu menangani Titik X saat perjalanan pulang.", 5),
              "C": ("Mengerjakan Titik Z paling ujung dulu karena sekalian jalan jauh.", 2),
              "D": ("Kembali ke kantor setiap selesai 1 titik.", 1)}},
    {"id": 53, "sec": 8, "q": "53. [Analisis Akar Masalah Teknis] Sebuah lokasi selalu mengalami trip/mati setiap pukul 13.00–14.30 siang saat cuaca terik, namun selalu normal kembali di malam hari. Tegangan PLN dan kapasitas penyearah (rectifier) terukur normal. Hipotesis penalaran teknis yang paling tepat adalah:",
     "opts": {"A": ("Perangkat terkena gangguan mistis di siang hari.", 0),
              "B": ("Terjadi over-temperature (suhu ruang perangkat/kabinet terlalu panas pada puncak terik siang hari akibat pendingin/fan bermasalah atau ventilasi tersumbat) yang memicu proteksi termal.", 5),
              "C": ("Kabel optik putus setiap jam 1 siang lalu menyambung sendiri malam hari.", 1),
              "D": ("Aki stater genset habis setiap siang hari.", 2)}},
    {"id": 54, "sec": 8, "q": "54. [Penalaran Anomali Data] Dalam laporan pengajuan BBM, Teknisi B menginput KM Awal: 45.200 dan KM Akhir: 45.450 (selisih 250 km) untuk perjalanan pergi-pulang dari Kantor ke Site M. Padahal jarak peta dari Kantor ke Site M hanya 30 km (pergi-pulang 60 km). Analisis logis Anda?",
     "opts": {"A": ("Langsung menyetujui karena malas menghitung selisih angka.", 1),
              "B": ("Menolak/menahan verifikasi karena terdapat anomali jarak ekstrem (selisih 190 km dari kewajaran), lalu memeriksa bukti foto odometer dengan koordinat lokasi serta mengonfirmasi apakah ada rute pengalihan resmi atau salah ketik/kecurangan.", 5),
              "C": ("Langsung menuduh teknisi mencuri tanpa memeriksa foto odometer terlebih dahulu.", 2),
              "D": ("Mengurangi sendiri nominal uangnya tanpa bertanya.", 2)}},
    {"id": 55, "sec": 8, "q": "55. [Penalaran Kapasitas & Beban] Sebuah sistem baterai cadangan 48V memiliki kapasitas sehat yang sanggup menahan beban 20 Ampere selama 4 jam. Jika karena penambahan perangkat baru beban lokasi meningkat menjadi 40 Ampere (dua kali lipat), maka secara logis estimasi waktu bertahan (backup time) baterai tersebut akan:",
     "opts": {"A": ("Tetap bertahan selama 4 jam karena baterainya sama.", 1),
              "B": ("Berkurang menjadi sekitar separuhnya (kurang lebih 2 jam atau sedikit di bawahnya), sehingga lokasi tersebut harus masuk prioritas pengawasan ketat saat listrik utama padam.", 5),
              "C": ("Meningkat menjadi 8 jam.", 1),
              "D": ("Langsung meledak saat itu juga.", 1)}},
    {"id": 56, "sec": 8, "q": "56. [Penalaran Pola Kesalahan SDM] Dari data 20 laporan yang salah input bulan ini, Anda menemukan 16 kesalahan berasal dari bagian pengisian 'Parameter Baterai' oleh 4 teknisi yang berbeda. Kesimpulan manajerial yang paling logis dari pola data ini adalah:",
     "opts": {"A": ("Keempat teknisi tersebut sengaja bersekongkol untuk merusak laporan.", 1),
              "B": ("Ada ketidakjelasan pada format form/instruksi kerja atau kurangnya pemahaman standar cara ukur baterai di tim, sehingga solusinya adalah menyeragamkan panduan cara ukur & input untuk seluruh tim.", 5),
              "C": ("Memecat keempat teknisi tersebut secara bersamaan.", 1),
              "D": ("Menghapus kolom Parameter Baterai dari laporan.", 2)}},
    {"id": 57, "sec": 8, "q": "57. [Penyelesaian Masalah Keterbatasan Alat] Tim Anda harus mengecek 2 lokasi berbeda secara paralel di waktu yang sama, namun alat ukur khusus yang akurat di kantor hanya tersisa 1 unit, sementara lokasi A berjarak 10 menit dari lokasi B. Solusi pengaturan paling efektif adalah:",
     "opts": {"A": ("Membatalkan pengecekan lokasi B dan membiarkannya terbengkalai.", 1),
              "B": ("Mengatur sinkronisasi tahapan kerja: Tim di Lokasi A melakukan pengukuran terlebih dahulu sementara Tim di Lokasi B menyiapkan pembersihan fisik/visual; begitu selesai diukur (15 menit), alat ukur langsung digeser ke Lokasi B yang berdekatan.", 5),
              "C": ("Menyuruh Tim Lokasi B mengarang angka pengukuran tanpa alat.", 0),
              "D": ("Menunggu bulan depan sampai alat baru dibelikan.", 1)}},
    {"id": 58, "sec": 8, "q": "58. [Penalaran Sebab-Akibat] Sejak jadwal Preventive Maintenance (PM) diubah dari sekadar 'kunjungan formalitas' menjadi 'wajib cek kekencangan koneksi kabel & uji beban genset', jumlah tiket gangguan mendadak di malam hari turun hingga 60%. Kesimpulan strategis apa yang Anda ambil sebagai Leader?",
     "opts": {"A": ("Penurunan gangguan malam hari itu hanya kebetulan cuaca sedang bagus.", 2),
              "B": ("Kualitas eksekusi PM berbanding lurus dengan penurunan gangguan; oleh karena itu, pengawasan kualitas PM wajib dipertahankan secara ketat agar tim tidak perlu kelelahan menangani gangguan malam hari.", 5),
              "C": ("Mengurangi lagi kualitas PM bulan depan karena gangguan sudah jarang.", 1),
              "D": ("Tidak ada hubungan antara PM dan gangguan.", 1)}},
    {"id": 59, "sec": 8, "q": "59. [Pengambilan Keputusan Berbasis Risiko] Anda memiliki sisa anggaran pemeliharaan preventif bulan ini yang hanya cukup untuk memperbaiki 1 lokasi: Lokasi P (di dalam kota, akses mudah 10 menit, potensi gangguan sedang) atau Lokasi Q (di pedalaman seberang sungai, akses 4 jam perjalanan, kondisi komponen sudah aus kritis). Mana yang Anda dahulukan dan mengapa?",
     "opts": {"A": ("Lokasi P karena dekat dan cepat selesai sehingga Anda bisa cepat istirahat.", 1),
              "B": ("Lokasi Q, karena secara manajemen risiko, jika Lokasi Q sampai mati mendadak di malam hari, waktu tempuh dan biaya penanganannya akan jauh lebih besar serta berisiko melanggar SLA dibanding Lokasi P yang dekat.", 5),
              "C": ("Tidak memperbaiki keduanya agar anggaran utuh.", 1),
              "D": ("Membagi dua anggaran sehingga kedua lokasi hanya diperbaiki setengah-setengah dan tidak tuntas.", 2)}},
    {"id": 60, "sec": 8, "q": "60. [Integrasi Seluruh Karakter Leader] Jika Anda terpilih menjadi Team Leader, ukuran keberhasilan tertinggi Anda dalam 6 bulan pertama adalah:",
     "opts": {"A": ("Ditakuti oleh seluruh bawahan dan menjadi orang yang paling disayang Bos meskipun kinerja tim biasa saja.", 1),
              "B": ("Terbentuknya tim yang disiplin tanpa harus selalu diawasi, data operasional 100% akurat & jujur, target SLA tercapai konsisten, serta anggota tim berkembang secara skill dan sejahtera secara aturan.", 5),
              "C": ("Semua pekerjaan teknis lapangan Anda kerjakan sendiri tanpa melibatkan anggota tim.", 2),
              "D": ("Tidak pernah ada anggota tim yang mengeluh karena semua aturan dilonggarkan.", 1)}}
]

# ==========================================
# INISIALISASI STATE HALAMAN & TIMER
# ==========================================
if "step" not in st.session_state:
    st.session_state.step = 0  # 0 = Isi Identitas, 1..8 = Bagian 1..8, 9 = Selesai
if "nama" not in st.session_state:
    st.session_state.nama = ""
if "area" not in st.session_state:
    st.session_state.area = ""
if "all_answers" not in st.session_state:
    st.session_state.all_answers = {}
if "sec_start_time" not in st.session_state:
    st.session_state.sec_start_time = {}
if "overtime_log" not in st.session_state:
    st.session_state.overtime_log = {}

st.title("📋 Assessment Seleksi Calon Team Leader (60 Soal)")

# ==========================================
# TAHAP 0: HALAMAN IDENTITAS & PETUNJUK
# ==========================================
if st.session_state.step == 0:
    st.info(
        "### 📌 Petunjuk Pengerjaan Terstruktur\n"
        "Agar tidak memusingkan, 60 soal seleksi ini telah dikelompokkan menjadi **8 Bagian Berurutan (Bagian 1 s/d Bagian 8)**.\n\n"
        "- Setiap bagian memiliki **Batas Waktu (Countdown Timer)** di bagian atas layar sesuai tingkat kesulitan soal.\n"
        "- Pastikan Anda menjawab seluruh soal di bagian yang sedang aktif sebelum menekan tombol **Lanjut ke Bagian Berikutnya**.\n"
        "- Ketepatan waktu pengerjaan di setiap bagian akan tercatat secara otomatis di sistem penilaian."
    )
    
    with st.form("form_identitas"):
        col1, col2 = st.columns(2)
        with col1:
            inp_nama = st.text_input("Nama Lengkap Kandidat *", placeholder="Masukkan nama lengkap Anda")
        with col2:
            inp_area = st.text_input("Tim / Area Kerja *", placeholder="Contoh: Tim 1 - Palangkaraya")
            
        mulai_btn = st.form_submit_button("🚀 Mulai Kerjakan Bagian 1", use_container_width=True)
        
    if mulai_btn:
        if not inp_nama.strip() or not inp_area.strip():
            st.error("⚠️ Mohon isi Nama Lengkap dan Tim / Area Kerja terlebih dahulu!")
        else:
            st.session_state.nama = inp_nama.strip()
            st.session_state.area = inp_area.strip()
            st.session_state.step = 1
            st.session_state.sec_start_time[1] = time.time()
            st.rerun()

# ==========================================
# TAHAP 1 s/d 8: PENGERJAAN PER BAGIAN + TIMER
# ==========================================
elif 1 <= st.session_state.step <= 8:
    cur_sec = st.session_state.step
    sec_info = SECTIONS[cur_sec]
    
    if cur_sec not in st.session_state.sec_start_time:
        st.session_state.sec_start_time[cur_sec] = time.time()
        
    st.progress(cur_sec / 8.0, text=f"Progres Pengerjaan: Bagian {cur_sec} dari 8 Bagian ({int((cur_sec/8)*100)}%)")
    
    batas_detik = sec_info["minutes"] * 60
    waktu_berjalan = time.time() - st.session_state.sec_start_time[cur_sec]
    sisa_detik = max(0, int(batas_detik - waktu_berjalan))
    
    tampilkan_timer_visual(sisa_detik, cur_sec)
    
    st.subheader(sec_info["title"])
    st.caption(f"📌 {sec_info['desc']} | Alokasi Waktu: **{sec_info['minutes']} Menit**")
    st.divider()
    
    soal_bagian_ini = [q for q in QUESTIONS if q["sec"] == cur_sec]
    
    with st.form(f"form_bagian_{cur_sec}"):
        jawaban_sementara = {}
        for item in soal_bagian_ini:
            st.markdown(f"**{item['q']}**")
            options_display = [f"{k}. {v[0]}" for k, v in item["opts"].items()]
            selected = st.radio(
                f"Soal {item['id']}",
                options=options_display,
                index=None,
                key=f"q_{item['id']}",
                label_visibility="collapsed"
            )
            jawaban_sementara[item["id"]] = selected
            st.write("")
            
        label_tombol = f"➡️ Simpan & Lanjut ke Bagian {cur_sec + 1}" if cur_sec < 8 else "✅ Selesai & Kirim Seluruh Jawaban (60 Soal)"
        next_submitted = st.form_submit_button(label_tombol, use_container_width=True)
        
    if next_submitted:
        if None in jawaban_sementara.values():
            st.error(f"⚠️ Mohon jawab seluruh soal pada Bagian {cur_sec} ini sebelum melanjutkan!")
        else:
            durasi_aktual = time.time() - st.session_state.sec_start_time[cur_sec]
            lewat_waktu = durasi_aktual > (sec_info["minutes"] * 60 + 10)
            st.session_state.overtime_log[cur_sec] = {
                "durasi_menit": round(durasi_aktual / 60.0, 1),
                "batas_menit": sec_info["minutes"],
                "overtime": lewat_waktu
            }
            
            for qid, val in jawaban_sementara.items():
                st.session_state.all_answers[qid] = val
                
            if cur_sec < 8:
                st.session_state.step = cur_sec + 1
                st.session_state.sec_start_time[cur_sec + 1] = time.time()
                st.rerun()
            else:
                st.session_state.step = 9
                st.rerun()

# ==========================================
# TAHAP 9: KALKULASI OTOMATIS & KIRIM KE APPS SCRIPT
# ==========================================
elif st.session_state.step == 9:
    if "sudah_disimpan" not in st.session_state:
        with st.spinner("Mengolah nilai dan mengirim data ke Google Spreadsheet 'Test Leader'..."):
            kat_scores = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0}
            detail_jawaban_sheet = []
            skor_murni = 0
            
            for item in QUESTIONS:
                qid = item["id"]
                sec_id = item["sec"]
                ans_str = st.session_state.all_answers.get(qid, "A. -")
                chosen_letter = ans_str.split(".")[0]
                teks_jawaban, pts = item["opts"][chosen_letter]
                
                kat_scores[sec_id] += pts
                skor_murni += pts
                detail_jawaban_sheet.append(f"Opsi {chosen_letter} ({pts} Poin) - {teks_jawaban}")
                
            penalti_waktu = 0
            info_waktu_list = []
            for s_idx in range(1, 9):
                log_w = st.session_state.overtime_log.get(s_idx, {})
                dur = log_w.get("durasi_menit", 0)
                bts = log_w.get("batas_menit", 0)
                if log_w.get("overtime", False):
                    penalti_waktu += 2
                    info_waktu_list.append(f"Bag {s_idx}: TELAT ({dur}/{bts} mnt)")
                else:
                    info_waktu_list.append(f"Bag {s_idx}: Tepat ({dur}/{bts} mnt)")
                    
            catatan_waktu_str = " | ".join(info_waktu_list)
            total_skor_akhir = max(0, skor_murni - penalti_waktu)
            
            if total_skor_akhir >= 255 and kat_scores[6] >= 20 and kat_scores[8] >= 38:
                status_lulus = "SANGAT DIREKOMENDASIKAN (Tegas, Cerdas & Berintegritas)"
            elif total_skor_akhir >= 215 and kat_scores[6] >= 18:
                status_lulus = "POTENSIAL DENGAN PENDAMPINGAN"
            else:
                status_lulus = "BELUM LAYAK (Kurang Tegas / Lemah Penalaran / Rawan Integritas)"
                
            remark_lengkap = buat_remark_karakter_60(kat_scores, penalti_waktu)
            waktu_skrg = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            
            row_to_save = [
                waktu_skrg,
                st.session_state.nama,
                st.session_state.area,
                total_skor_akhir,
                skor_murni,
                penalti_waktu,
                catatan_waktu_str,
                status_lulus,
                remark_lengkap,
                kat_scores[1],
                kat_scores[2],
                kat_scores[3],
                kat_scores[4],
                kat_scores[5],
                kat_scores[6],
                kat_scores[7],
                kat_scores[8]
            ] + detail_jawaban_sheet
            
            try:
                simpan_ke_spreadsheet(row_to_save)
                st.session_state.sudah_disimpan = True
            except Exception as e:
                st.error(f"Gagal mengirim ke Google Spreadsheet: {e}")

    if st.session_state.get("sudah_disimpan", False):
        st.balloons()
        st.success("🎉 Selamat! Anda telah menyelesaikan seluruh 8 Bagian (60 Soal) Assessment Calon Team Leader dan hasil Anda telah terekam di sistem.")
        
        pesan_wa = (
            f"Halo Pak, saya *{st.session_state.nama}* ({st.session_state.area}) "
            f"sudah mengisi dan menyelesaikan seluruh 8 Bagian (60 Soal) Assessment Calon Leader."
        )
        url_wa = f"https://wa.me/{NOMOR_WA_KOORDINATOR}?text={urllib.parse.quote(pesan_wa)}"
        
        st.link_button("📲 Klik di Sini untuk Konfirmasi ke WhatsApp (08115251515)", url_wa, use_container_width=True)
