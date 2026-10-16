import streamlit as st
import pandas as pd
import json
import base64
import urllib.parse
import requests
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

# ==========================================
# KONFIGURASI EVALUATOR & GOOGLE SHEETS
# ==========================================
EVALUATOR_EMAIL = "oktapradika57@gmail.com"          # Ganti dengan email resmi Anda
EVALUATOR_PIN = "123456"                          # PIN khusus membuka tab Ruang Evaluator
EVALUATOR_WA = "08115251515"                    # Nomor WA Anda (diawali 62)
APP_BASE_URL = "https://nama-app-anda.streamlit.app"  # URL aplikasi Streamlit Anda

SPREADSHEET_TITLE = "Request Operational NOP Palangkaraya (Jawaban)"
WORKSHEET_NAME = "Test Leader"

st.set_page_config(page_title="Assessment 35 Soal Calon Team Leader", page_icon="📋", layout="wide")

# ==========================================
# FUNGSI KONEKSI KE SHEET "Test Leader"
# ==========================================
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

HEADERS_TEST_LEADER = [
    "Timestamp", "Nama Kandidat", "Tim / Area", 
    "Total Skor (Max 175)", "Status Rekomendasi",
    "Skor Kepemimpinan (25)", "Skor Teknis (25)", 
    "Skor Sudut Pandang (25)", "Skor Problem Solving (25)",
    "Skor Kehidupan & Profesional (50)", "Skor Integritas & Ketegasan (25)"
] + [f"Soal {i}" for i in range(1, 36)] + ["Token Evaluasi"]

@st.cache_resource
def get_gspread_client():
    creds_dict = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    return gspread.authorize(creds)

def get_test_leader_worksheet():
    client = get_gspread_client()
    sh = client.open(SPREADSHEET_TITLE)
    try:
        ws = sh.worksheet(WORKSHEET_NAME)
    except gspread.exceptions.WorksheetNotFound:
        ws = sh.add_worksheet(title=WORKSHEET_NAME, rows=200, cols=50)
        
    existing_data = ws.get_all_values()
    if not existing_data or len(existing_data[0]) == 0 or existing_data[0][0] == "":
        ws.insert_row(HEADERS_TEST_LEADER, index=1, value_input_option="USER_ENTERED")
    return ws

def save_to_test_leader_sheet(payload_data, encrypted_token):
    ws = get_test_leader_worksheet()
    
    row_data = [
        payload_data["waktu"],
        payload_data["nama"],
        payload_data["area"],
        payload_data["total"],
        payload_data["status"],
        payload_data["kategori"]["Kepemimpinan"],
        payload_data["kategori"]["Teknis Operasional"],
        payload_data["kategori"]["Sudut Pandang"],
        payload_data["kategori"]["Pola Pikir & Problem Solving"],
        payload_data["kategori"]["Kehidupan Pribadi & Profesional"],
        payload_data["kategori"]["Integritas & Ketegasan"]
    ]
    
    for i in range(1, 36):
        ans_info = payload_data["detail"].get(str(i), {})
        opt = ans_info.get("pilih", "-")
        pts = ans_info.get("poin", 0)
        row_data.append(f"{opt} ({pts})")
        
    row_data.append(encrypted_token)
    ws.append_row(row_data, value_input_option="USER_ENTERED")
    return True

def load_data_from_test_leader():
    ws = get_test_leader_worksheet()
    records = ws.get_all_records()
    return pd.DataFrame(records)

# ==========================================
# FUNGSI ENKRIPSI & DEKRIPSI
# ==========================================
def encrypt_payload(data_dict, key_email):
    raw_json = json.dumps(data_dict)
    key = key_email.strip().lower()
    xored = ''.join(chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(raw_json))
    return base64.urlsafe_b64encode(xored.encode('utf-8')).decode('utf-8')

def decrypt_payload(token_str, input_email):
    try:
        key = input_email.strip().lower()
        xored = base64.urlsafe_b64decode(token_str.encode('utf-8')).decode('utf-8')
        raw_json = ''.join(chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(xored))
        return json.loads(raw_json)
    except Exception:
        return None

# ==========================================
# DATABASE 35 SOAL LENGKAP
# ==========================================
QUESTIONS = [
    # I. KEPEMIMPINAN (1-5)
    {"id": 1, "cat": "Kepemimpinan", "q": "1. Di tim Anda terdapat dua anggota: Anggota A cepat teknis tapi lemah administrasi, Anggota B rapi administrasi tapi lambat teknis. Saat ada pekerjaan mendesak, bagaimana Anda mengatur mereka?",
     "opts": {"A": ("Menugaskan Anggota A mengerjakan semuanya, meminta B buat laporan dari kantor.", 2),
              "B": ("Memasangkan keduanya: A fokus eksekusi teknis, B mendampingi untuk memastikan kelengkapan data real-time sambil belajar.", 5),
              "C": ("Menurunkan tangan sendiri mengerjakan bagian terberat agar tidak pusing.", 3),
              "D": ("Menegur keras keduanya sebelum berangkat agar tidak mengulangi kelemahan.", 1)}},
    {"id": 2, "cat": "Kepemimpinan", "q": "2. Anggota tim senior berkeahlian tinggi berulang kali terlambat melengkapi laporan dan meremehkan administrasi. Apa tindakan Anda?",
     "opts": {"A": ("Memakluminya selama teknis aman, lalu membantu melengkapi laporannya.", 2),
              "B": ("Memanggil empat mata, mengapresiasi skill-nya, namun menegaskan pekerjaan belum selesai (0%) jika laporan belum masuk, serta menetapkan konsekuensi.", 5),
              "C": ("Langsung melaporkannya ke Koordinator agar diberi SP tanpa diskusi.", 3),
              "D": ("Menyindirnya di grup WhatsApp tim agar dia merasa malu.", 1)}},
    {"id": 3, "cat": "Kepemimpinan", "q": "3. Tim Anda gagal mencapai target SLA karena kesalahan salah satu anggota. Saat dievaluasi atasan, apa yang Anda sampaikan?",
     "opts": {"A": ("Menyebutkan nama anggota yang bersalah secara langsung agar atasan tahu bukan salah Anda.", 1),
              "B": ("Mengambil tanggung jawab penuh sebagai Leader, menjelaskan akar masalah secara objektif, dan memaparkan langkah pencegahan ke depan.", 5),
              "C": ("Menyalahkan faktor eksternal seperti cuaca atau peralatan kurang mendukung.", 2),
              "D": ("Meminta anggota tersebut menghadap atasan sendirian untuk menjelaskan kesalahannya.", 3)}},
    {"id": 4, "cat": "Kepemimpinan", "q": "4. Tim harus menangani gangguan darurat malam hari saat cuaca buruk, sementara anggota mulai mengeluh kelelahan. Sikap Anda?",
     "opts": {"A": ("Memerintahkan tetap berangkat sambil dipantau lewat telepon tiap jam.", 3),
              "B": ("Hadir langsung memimpin/memastikan logistik & keamanan, memberi arahan tenang, serta mengatur rotasi istirahat.", 5),
              "C": ("Menunda pekerjaan sampai besok pagi tanpa koordinasi karena kasihan.", 2),
              "D": ("Mengancam memotong penilaian kinerja jika masih mengeluh.", 1)}},
    {"id": 5, "cat": "Kepemimpinan", "q": "5. Anggota tim baru belum menguasai troubleshooting utama di tengah jadwal padat. Langkah yang Anda ambil?",
     "opts": {"A": ("Membiarkannya belajar sendiri melihat anggota lain bekerja.", 2),
              "B": ("Membuatkan panduan checklist SOP, memasangkannya dengan senior, dan mengevaluasi 15-20 menit seusai kerja.", 5),
              "C": ("Hanya memberinya tugas ringan terus-menerus agar tidak menghambat.", 1),
              "D": ("Meminta atasan menukar anggota tersebut dengan yang berpengalaman.", 3)}},

    # II. TEKNIS OPERASIONAL (6-10)
    {"id": 6, "cat": "Teknis Operasional", "q": "6. Muncul 3 tiket bersamaan: (1) A: listrik padam baterai 90% sehat, (2) B: DC drop kritis genset gagal start, (3) C: PM rutin. Urutan prioritas yang tepat:",
     "opts": {"A": ("Lokasi C -> Lokasi A -> Lokasi B (menyelesaikan yang rutin dulu).", 1),
              "B": ("Lokasi B -> Lokasi A -> Lokasi C (amankan titik kritis dulu, pantau A, lalu jadwalkan PM).", 5),
              "C": ("Lokasi A -> Lokasi B -> Lokasi C (karena tiket A masuk lebih dulu).", 3),
              "D": ("Menunggu instruksi atasan tanpa menggerakkan tim.", 2)}},
    {"id": 7, "cat": "Teknis Operasional", "q": "7. Genset gagal menyala otomatis saat listrik padam dan muncul alarm gagal crank. Langkah pemeriksaan teknis pertama yang sistematis:",
     "opts": {"A": ("Langsung membongkar mesin atau mengganti modul kontrol tanpa cek dasar.", 2),
              "B": ("Memeriksa parameter dasar berurutan: tegangan aki, BBM & jalur solenoid, tombol Emergency/Auto, lalu coba manual start.", 5),
              "C": ("Me-reset alarm berulang kali sampai aki habis dengan harapan menyala sendiri.", 1),
              "D": ("Langsung menyimpulkan genset rusak berat dan meninggalkan lokasi.", 3)}},
    {"id": 8, "cat": "Teknis Operasional", "q": "8. Anggota mengirim laporan PM dengan waktu sangat cepat, namun angka & foto dokumentasi sangat mirip bulan lalu. Tindakan Anda?",
     "opts": {"A": ("Langsung menyetujui agar target kuantitas harian tercapai.", 1),
              "B": ("Menahan laporan, memeriksa metadata foto & histori parameter, serta mewajibkan pengukuran ulang valid via video call/kunjungan.", 5),
              "C": ("Mengubah sendiri angka di laporan agar sedikit berbeda.", 2),
              "D": ("Menghapus laporan tersebut tanpa memberitahu anggota.", 3)}},
    {"id": 9, "cat": "Teknis Operasional", "q": "9. Sebelum tim berangkat penanganan gangguan berjarak 3 jam, prosedur kesiapan teknis apa yang wajib dipastikan Leader?",
     "opts": {"A": ("Cukup pastikan mobil isi bensin dan membawa tas kerja masing-masing.", 3),
              "B": ("Memeriksa alat ukur berfungsi, kelengkapan tools, sparepart sesuai gejala, serta kesiapan APD/K3.", 5),
              "C": ("Meminta tim langsung berangkat tanpa cek alat agar terlihat responsif.", 2),
              "D": ("Menyerahkan sepenuhnya ke teknisi tanpa verifikasi.", 1)}},
    {"id": 10, "cat": "Teknis Operasional", "q": "10. Sisa 15 menit sebelum SLA habis, anggota meminta izin melompati prosedur K3 demi mempercepat pekerjaan. Keputusan Anda?",
     "opts": {"A": ("Mengizinkan khusus kali ini yang penting SLA tidak lewat.", 2),
              "B": ("Menolak tegas, wajib jalankan K3, sambil laporkan kondisi riil ke Koordinator bahwa keselamatan adalah prioritas.", 5),
              "C": ("Menyuruh teknisi melakukannya diam-diam asal tak terekam foto.", 1),
              "D": ("Menghentikan seluruh pekerjaan dan menyuruh tim pulang.", 3)}},

    # III. SUDUT PANDANG (11-15)
    {"id": 11, "cat": "Sudut Pandang", "q": "11. Manajemen mewajibkan update laporan lengkap di sistem sebelum pencairan dana operasional berikutnya. Anggota mengeluh menghambat. Sikap Anda?",
     "opts": {"A": ("Ikut mengeluh dan menyalahkan aturan manajemen.", 1),
              "B": ("Memahami pentingnya akuntabilitas data, mendisiplinkan tim agar langsung submit laporan begitu pekerjaan selesai sehingga dana tidak terkunci.", 5),
              "C": ("Mencari celah menginput data kosong/palsu asal dana cair.", 2),
              "D": ("Membiarkan anggota protes ke admin tanpa memberikan solusi.", 3)}},
    {"id": 12, "cat": "Sudut Pandang", "q": "12. Saat di lokasi menyelesaikan tiket ringan, Anda melihat anomali kabel panas pada perangkat lain yang belum ada tiket tapi berpotensi down. Tindakan Anda?",
     "opts": {"A": ("Mengabaikannya karena bukan ruang lingkup tiket hari ini.", 2),
              "B": ("Melakukan tindakan pencegahan aman saat itu, dokumentasikan foto & data, dan laporkan sebagai preventive maintenance.", 5),
              "C": ("Menunggu sampai perangkat benar-benar rusak dan memunculkan tiket baru.", 1),
              "D": ("Hanya memfotonya dan disimpan di HP pribadi.", 3)}},
    {"id": 13, "cat": "Sudut Pandang", "q": "13. Atasan menegur karena data laporan tim Anda banyak salah ketik dibanding area lain. Cara Anda menyikapinya?",
     "opts": {"A": ("Merasa tersinggung karena tim sudah bekerja keras secara fisik.", 2),
              "B": ("Menerima koreksi, mengecek kesalahan input, dan menerapkan verifikasi silang (double-check) sebelum data dikirim.", 5),
              "C": ("Berdebat bahwa akurasi data tidak penting selama perangkat menyala.", 1),
              "D": ("Memarahi admin atau anggota di depan umum untuk melampiaskan kesal.", 3)}},
    {"id": 14, "cat": "Sudut Pandang", "q": "14. Terdapat sisa material/dana operasional setelah perbaikan, dan anggota mengusulkan tidak usah dilaporkan untuk uang makan. Sikap Anda?",
     "opts": {"A": ("Menyetujuinya selama jumlahnya kecil.", 1),
              "B": ("Menolak tegas, menegaskan integritas adalah harga mati, dan melaporkan seluruh sisa secara transparan.", 5),
              "C": ("Pura-pura tidak tahu dan menyerahkan pada anggota.", 2),
              "D": ("Mengambil sisa tersebut untuk disimpan sendiri.", 1)}},
    {"id": 15, "cat": "Sudut Pandang", "q": "15. Terjadi selisih data rekap lapangan dengan catatan Admin Operasional. Sudut pandang Anda dalam menyelesaikannya?",
     "opts": {"A": ("Menganggap admin tidak becus dan menyerang admin di grup.", 1),
              "B": ("Memandang admin sebagai mitra, melakukan rekonsiliasi baik-baik menyandingkan bukti lapangan (log, foto, jam check-in).", 5),
              "C": ("Mengabaikan rekap admin karena merasa catatan lapangan pasti benar.", 2),
              "D": ("Meminta atasan menegur admin tanpa mengecek data tim sendiri.", 3)}},

    # IV. POLA PIKIR & PROBLEM SOLVING (16-20)
    {"id": 16, "cat": "Pola Pikir & Problem Solving", "q": "16. Lokasi mengalami gangguan berulang 3x sebulan dengan gejala sama, teknisi selama ini hanya mereset dan normal sementara. Pola pikir Anda:",
     "opts": {"A": ("Tetap lakukan reset tiap gangguan muncul karena paling cepat.", 2),
              "B": ("Hentikan pola tambal sulam; lakukan Root Cause Analysis (analisis tren beban, tegangan, suhu) untuk solusi permanen.", 5),
              "C": ("Menyalahkan kualitas perangkat tua tanpa pengukuran data.", 3),
              "D": ("Meminta lokasi tersebut dipindah ke tim lain.", 1)}},
    {"id": 17, "cat": "Pola Pikir & Problem Solving", "q": "17. Di tengah perjalanan ke gangguan kritis, kendaraan mogok dan sparepart kurang satu komponen. Cara Anda menyelesaikan masalah ganda ini:",
     "opts": {"A": ("Membatalkan perjalanan dan kembali ke kantor menunggu besok.", 2),
              "B": ("Membagi fokus taktis: satu orang urus kendaraan/transport alternatif, Anda berkoordinasi dengan rekan/toko teknik untuk komponen serta update estimasi waktu ke Koordinator.", 5),
              "C": ("Panik dan mematikan komunikasi karena takut dimarahi.", 1),
              "D": ("Memaksakan kendaraan rusak parah jalan terus membahayakan nyawa.", 3)}},
    {"id": 18, "cat": "Pola Pikir & Problem Solving", "q": "18. Anda diberi akses histori data daya, baterai, dan gangguan 3 bulan. Bagaimana Anda memanfaatkannya?",
     "opts": {"A": ("Hanya disimpan sebagai arsip jika ditanya saat audit.", 3),
              "B": ("Memetakan lokasi penurunan performa tajam untuk dijadikan prioritas jadwal kunjungan pencegahan sebelum down.", 5),
              "C": ("Bingung membacanya dan menyerahkan seluruh analisis ke atasan.", 2),
              "D": ("Hanya melihat lokasi yang kondisinya bagus untuk dilaporkan.", 1)}},
    {"id": 19, "cat": "Pola Pikir & Problem Solving", "q": "19. Dua anggota berdebat keras soal letak kerusakan hingga pekerjaan terhenti. Cara Anda mengurai masalah:",
     "opts": {"A": ("Membiarkan berdebat sampai salah satu mengalah sendiri.", 2),
              "B": ("Menengahi kepala dingin, hentikan asumsi, arahkan pembuktian berbasis pengukuran alat ukur satu persatu secara objektif.", 5),
              "C": ("Membela anggota yang lebih dekat secara pribadi tanpa cek perangkat.", 1),
              "D": ("Memulangkan keduanya dan dikerjakan sendiri.", 3)}},
    {"id": 20, "cat": "Pola Pikir & Problem Solving", "q": "20. Rencana kerja mingguan harus berubah di hari Rabu karena ada instruksi audit mendadak di beberapa titik. Cara Anda beradaptasi:",
     "opts": {"A": ("Menolak instruksi baru karena jadwal mingguan tidak boleh diubah.", 1),
              "B": ("Re-planning cepat: gabungkan rute searah target rutin dan mendadak, atur ulang skala prioritas, dan komunikasikan ke atasan.", 5),
              "C": ("Menghentikan seluruh pekerjaan rutin seminggu penuh.", 2),
              "D": ("Bekerja acak tanpa perencanaan karena merasa menyusun jadwal sia-sia.", 3)}},

    # V. KEHIDUPAN PRIBADI & PROFESIONAL (21-30)
    {"id": 21, "cat": "Kehidupan Pribadi & Profesional", "q": "21. Anggota tim sering menghubungi Anda tengah malam untuk curhat non-darurat. Batasan komunikasi profesional yang Anda terapkan?",
     "opts": {"A": ("Memarahi dan memblokir nomor anggota agar tidak mengganggu istirahat.", 1),
              "B": ("Menetapkan norma komunikasi: siap tanggap untuk darurat operasional, namun mengarahkan hal non-darurat dibahas pada jam kerja esok hari.", 5),
              "C": ("Selalu melayani obrolan pribadi mereka sampai larut malam setiap hari.", 2),
              "D": ("Mengabaikan semua panggilan selamanya termasuk panggilan darurat lapangan.", 1)}},
    {"id": 22, "cat": "Kehidupan Pribadi & Profesional", "q": "22. Performa anggota tim menurun drastis karena masalah keluarga/finansial berat di rumah. Sikap Anda sebagai leader:",
     "opts": {"A": ("Memecatnya langsung karena dianggap tidak profesional.", 1),
              "B": ("Memanggil empat mata dengan empati, mendengarkan kondisinya, memberikan dukungan/penyesuaian tugas sementara, namun tetap menjaga target kerja.", 5),
              "C": ("Membiarkan dan memotong gajinya tiap kali hasil kerja jelek.", 2),
              "D": ("Ikut mencampuri dan menggosipkan masalah pribadinya ke tim lain.", 1)}},
    {"id": 23, "cat": "Kehidupan Pribadi & Profesional", "q": "23. Menjelang akhir pekan saat libur bersama keluarga, ada laporan minor dari lapangan yang bisa ditangani teknisi piket. Keputusan Anda?",
     "opts": {"A": ("Meninggalkan keluarga dan turun tangan sendiri ke lapangan.", 2),
              "B": ("Mempercayakan ke teknisi piket, pantau secara jarak jauh via sistem, biarkan sistem berjalan dan tetap siaga jika ada eskalasi.", 5),
              "C": ("Mematikan HP dan pura-pura tidak tahu ada masalah.", 1),
              "D": ("Memarahi teknisi piket karena berani menelepon di hari libur.", 1)}},
    {"id": 24, "cat": "Kehidupan Pribadi & Profesional", "q": "24. Salah satu anggota tim adalah teman dekat/kerabat Anda di luar kantor. Bagaimana cara Anda memperlakukan kinerjanya?",
     "opts": {"A": ("Memberikan dispensasi khusus, memaklumi keterlambatan dan meringankan laporan.", 1),
              "B": ("Tetap objektif dan profesional: memberlakukan standar aturan, teguran, dan penilaian yang persis sama tanpa keistimewaan.", 5),
              "C": ("Menjaganya agar tidak disentuh pekerjaan berat agar pertemanan tidak rusak.", 2),
              "D": ("Justru memberi beban paling berat untuk membuktikan tidak pilih kasih.", 3)}},
    {"id": 25, "cat": "Kehidupan Pribadi & Profesional", "q": "25. Anda sedang stres berat akibat tekanan atasan, lalu anggota tim membuat kesalahan sepele di lapangan. Cara Anda mengendalikan emosi:",
     "opts": {"A": ("Melampiaskan kemarahan dari atasan kepada anggota tim tersebut.", 1),
              "B": ("Memisahkan emosi: tenangkan diri, tegur kesalahan secara objektif terfokus pada perbaikan, susun strategi lapor atasan tanpa amarah.", 5),
              "C": ("Diam memendam stres sampai jatuh sakit.", 2),
              "D": ("Mengancam resign di depan tim karena tidak tahan tekanan.", 1)}},
    {"id": 26, "cat": "Kehidupan Pribadi & Profesional", "q": "26. Anggota tim sering menyindir manajemen atau menyebar info internal di status media sosial pribadinya. Tindakan Anda:",
     "opts": {"A": ("Ikut menyukai atau mengomentari postingan tersebut.", 1),
              "B": ("Menegur pribadi, jelaskan dampak pelanggaran kerahasiaan & etika profesional, minta postingan dihapus demi nama baik tim.", 5),
              "C": ("Membalas menyindir secara terbuka di media sosial.", 1),
              "D": ("Pura-pura tidak melihat karena medsos adalah hak pribadi.", 2)}},
    {"id": 27, "cat": "Kehidupan Pribadi & Profesional", "q": "27. Terjadi down total di wilayah kerja saat Anda harus menghadiri acara keluarga penting. Sikap Anda:",
     "opts": {"A": ("Mengabaikan kantor dan tetap di acara keluarga sepenuhnya.", 1),
              "B": ("Mengomunikasikan situasi ke keluarga, turun tangan/koordinasi darurat jarak jauh hingga sistem pulih, lalu atur waktu keluarga setelahnya.", 5),
              "C": ("Memarahi keluarga karena mengadakan acara di saat jadwal kerja berantakan.", 1),
              "D": ("Meminta anggota selesaikan sendiri, Anda acuh tak acuh.", 2)}},
    {"id": 28, "cat": "Kehidupan Pribadi & Profesional", "q": "28. Mulai terbentuk kubu-kubuan di dalam tim yang saling tidak akur. Cara Anda mengatasinya:",
     "opts": {"A": ("Memihak salah satu kubu yang lebih sering membantu Anda.", 1),
              "B": ("Mengadakan pertemuan, tegaskan tim hanya satu kesatuan, fokus pada target bersama, tindak tegas perilaku toksik.", 5),
              "C": ("Membiarkan bersaing tidak sehat karena mengira memotivasi.", 2),
              "D": ("Ikut membicarakan keburukan kubu sebelah.", 1)}},
    {"id": 29, "cat": "Kehidupan Pribadi & Profesional", "q": "29. Beredar gosip di tim bahwa tunjangan/libur akan dipotong manajemen pusat sehingga tim resah. Tindakan Anda:",
     "opts": {"A": ("Ikut memanaskan situasi dan menyebarkan gosip.", 1),
              "B": ("Meredam keresahan, konfirmasi fakta valid ke atasan/admin, sampaikan penjelasan transparan menenangkan berdasarkan data resmi.", 5),
              "C": ("Mendiamkan sampai tim melakukan mogok kerja.", 1),
              "D": ("Mengancam memecat siapa saja yang membicarakan gosip.", 2)}},
    {"id": 30, "cat": "Kehidupan Pribadi & Profesional", "q": "30. Evaluasi diri (Self-Leadership) apa yang rutin Anda lakukan setiap akhir bulan?",
     "opts": {"A": ("Merasa diri paling benar karena tidak pernah ditegur atasan.", 1),
              "B": ("Refleksi objektif: review pencapaian, evaluasi kekurangan kepemimpinan diri, aktif minta masukan Koordinator/Admin untuk perbaikan.", 5),
              "C": ("Menyalahkan seluruh kegagalan murni kebodohan anggota lapangan.", 2),
              "D": ("Menunggu ada yang memuji baru merasa puas.", 1)}},

    # VI. INTEGRITAS & KETEGASAN / PEMECATAN (31-35)
    {"id": 31, "cat": "Integritas & Ketegasan", "q": "31. Anda menemukan teknisi berkeahlian tinggi melakukan pemalsuan data KM dan manipulasi nota BBM untuk keuntungan pribadi. Tindakan tegas Anda:",
     "opts": {"A": ("Memakluminya karena tenaganya masih sangat dibutuhkan di lapangan.", 1),
              "B": ("Tegakkan integritas tanpa kompromi: proses sanksi berat / rekomendasi pemecatan karena kejujuran mutlak di atas keahlian.", 5),
              "C": ("Hanya tegur lisan asal berjanji tidak mengulangi tanpa sanksi tertulis.", 2),
              "D": ("Meminta bagian uang hasil manipulasi agar Anda tutup mulut.", 0)}},
    {"id": 32, "cat": "Integritas & Ketegasan", "q": "32. Anggota tim secara terbuka menolak instruksi kerja resmi, menantang otoritas Anda, dan membangkang. Langkah tegas Anda:",
     "opts": {"A": ("Menangis atau diam saja karena takut dimusuhi.", 1),
              "B": ("Tegur keras tertutup, catat pembangkangan tertulis, laporkan ke Koordinator, dan proses rekomendasi pemecatan jika tidak berubah demi wibawa tim.", 5),
              "C": ("Membiarkan membangkang asal perangkat lapangan menyala.", 2),
              "D": ("Membalas membentak dan memukul meja berisiko kekerasan fisik.", 1)}},
    {"id": 33, "cat": "Integritas & Ketegasan", "q": "33. Anggota tim sering menggunakan bahasa kasar, merendahkan rekan lain, atau menantang di grup WhatsApp resmi. Tindakan Anda:",
     "opts": {"A": ("Ikut tertawa dan membiarkan agar suasana grup santai.", 1),
              "B": ("Tegur tegas di grup bahwa ada norma kesopanan & etika profesional, bina empat mata, beri SP jika diulangi.", 5),
              "C": ("Keluar dari grup WhatsApp karena tidak tahan.", 2),
              "D": ("Memblokir anggota tanpa peringatan atau penjelasan.", 1)}},
    {"id": 34, "cat": "Integritas & Ketegasan", "q": "34. Pihak vendor memberikan sejumlah uang/fasilitas khusus agar laporan audit dipercepat atau anomali ditutup-tutupi. Sikap Anda:",
     "opts": {"A": ("Menerima dan membagikannya diam-diam ke tim.", 0),
              "B": ("Tolak tegas, edukasi tim bahwa suap/pungli mencoreng perusahaan dan berujung pemecatan seketika, laporkan ke manajemen.", 5),
              "C": ("Pura-pura tidak tahu asal Anda tidak ikut tanda tangan.", 1),
              "D": ("Memarahi pemberi suap dengan nada kasar di depan umum.", 2)}},
    {"id": 35, "cat": "Integritas & Ketegasan", "q": "35. Anggota sudah 3 kali diberi SP terkait pembangkangan, manipulasi data, dan pelanggaran etika komunikasi yang merusak tim. Keputusan akhir Anda:",
     "opts": {"A": ("Terus memberi kesempatan ke-4 dan ke-5 karena kasihan.", 1),
              "B": ("Ajukan rekomendasi pemecatan terstruktur ke manajemen melampirkan rekam jejak objektif, karena individu toksik & pembangkang harus dibersihkan.", 5),
              "C": ("Mengeluarkan dari grup WhatsApp kantor saja tanpa lapor HR/Koordinator.", 2),
              "D": ("Menurunkan gajinya secara sepihak tanpa prosedur resmi.", 1)}}
]

query_params = st.query_params
incoming_token = query_params.get("token", "")

st.title("📋 Seleksi 35 Soal Calon Team Leader (Integritas & Profesional)")

tab_kandidat, tab_evaluator = st.tabs(["📝 Lembar Kerja Kandidat", "🔒 Ruang Evaluator (Khusus Koordinator)"])

# ==========================================
# TAB 1: FORM KANDIDAT
# ==========================================
with tab_kandidat:
    st.info("Silakan isi data diri dan selesaikan 35 soal situasi kerja, kepemimpinan, integritas, dan etika profesional berikut.")
    
    with st.form("form_interview_35"):
        col1, col2 = st.columns(2)
        with col1:
            nama_kandidat = st.text_input("Nama Lengkap Kandidat *", placeholder="Contoh: Budi Santoso")
        with col2:
            tim_area = st.text_input("Tim / Cluster Area *", placeholder="Contoh: Tim Palangkaraya")
            
        st.divider()
        
        answers = {}
        for item in QUESTIONS:
            st.markdown(f"**{item['q']}**")
            options_display = [f"{k}. {v[0]}" for k, v in item["opts"].items()]
            selected = st.radio(
                f"Pilih jawaban Soal {item['id']}:",
                options=options_display,
                index=None,
                key=f"q_{item['id']}",
                label_visibility="collapsed"
            )
            answers[item["id"]] = selected
            st.write("")
            
        submitted = st.form_submit_button("✅ Kirim 35 Jawaban Interview", use_container_width=True)
        
    if submitted:
        if not nama_kandidat.strip() or not tim_area.strip() or None in answers.values():
            st.error("⚠️ Mohon lengkapi Nama, Area Kerja, dan pastikan seluruh 35 soal telah terjawab!")
        else:
            with st.spinner("Menyimpan hasil ke Google Sheets 'Test Leader'..."):
                cat_scores = {
                    "Kepemimpinan": 0,
                    "Teknis Operasional": 0,
                    "Sudut Pandang": 0,
                    "Pola Pikir & Problem Solving": 0,
                    "Kehidupan Pribadi & Profesional": 0,
                    "Integritas & Ketegasan": 0
                }
                detail_ans = {}
                total_score = 0
                
                for item in QUESTIONS:
                    qid = item["id"]
                    chosen_letter = answers[qid].split(".")[0]
                    pts = item["opts"][chosen_letter][1]
                    cat_scores[item["cat"]] += pts
                    total_score += pts
                    detail_ans[str(qid)] = {"pilih": chosen_letter, "poin": pts}
                    
                if total_score >= 150:
                    status_rek = "SANGAT DIREKOMENDASIKAN (Leader Tangguh & Berintegritas)"
                elif total_score >= 125:
                    status_rek = "POTENSIAL DENGAN PENDAMPINGAN KETAT"
                else:
                    status_rek = "TIDAK LAYAK (Lemah Integritas / Pembangkang)"
                    
                payload_data = {
                    "nama": nama_kandidat.strip(),
                    "area": tim_area.strip(),
                    "waktu": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                    "total": total_score,
                    "status": status_rek,
                    "kategori": cat_scores,
                    "detail": detail_ans
                }
                
                encrypted_token = encrypt_payload(payload_data, EVALUATOR_EMAIL)
                secret_link = f"{APP_BASE_URL}/?token={urllib.parse.quote(encrypted_token)}"
                
                sheet_saved = False
                try:
                    save_to_test_leader_sheet(payload_data, encrypted_token)
                    sheet_saved = True
                except Exception as e:
                    st.warning(f"Penyimpanan cadangan aktif ({e})")
                
                try:
                    requests.post(
                        f"https://formsubmit.co/ajax/{EVALUATOR_EMAIL}",
                        json={
                            "_subject": f"[TEST LEADER 35 SOAL] {nama_kandidat} - Skor: {total_score}/175",
                            "Nama_Kandidat": nama_kandidat,
                            "Area_Tim": tim_area,
                            "Total_Skor": f"{total_score} / 175 ({status_rek})",
                            "Skor_Integritas": f"{cat_scores['Integritas & Ketegasan']} / 25",
                            "Status_Sheet": "Tersimpan di Test Leader" if sheet_saved else "Via Token Link",
                            "Link_Buka_Detail": secret_link
                        },
                        timeout=5
                    )
                except Exception:
                    pass
                    
            st.success("🎉 Jawaban Anda berhasil dikirim! Silakan klik tombol WhatsApp di bawah untuk konfirmasi ke Koordinator.")
            
            wa_message = (
                f"Halo Pak, saya *{nama_kandidat}* ({tim_area}) telah merampungkan 35 Soal Assessment Leader.\n\n"
                f"✅ Data tersimpan di Sheet *Test Leader*.\n"
                f"🔗 *Link Buka Skor (Khusus Koordinator):*\n{secret_link}"
            )
            wa_url = f"https://wa.me/{EVALUATOR_WA}?text={urllib.parse.quote(wa_message)}"
            st.link_button("📲 Kirim Konfirmasi Selesai via WhatsApp", wa_url, use_container_width=True)

# ==========================================
# TAB 2: RUANG EVALUATOR
# ==========================================
with tab_evaluator:
    st.subheader("🔐 Dashboard Evaluasi Sheet `Test Leader` (35 Soal)")
    st.caption("Masukkan Email Resmi Anda dan PIN untuk melihat hasil rekapitulasi.")
    
    col_auth1, col_auth2 = st.columns(2)
    with col_auth1:
        input_email_eval = st.text_input("Email Resmi Koordinator:", placeholder="Masukkan email Anda...")
    with col_auth2:
        input_pin_eval = st.text_input("PIN Evaluator:", type="password", placeholder="Masukkan PIN...")
        
    is_authorized = (
        input_email_eval.strip().lower() == EVALUATOR_EMAIL.strip().lower() 
        and input_pin_eval.strip() == EVALUATOR_PIN
    )
    
    if input_email_eval or input_pin_eval:
        if not is_authorized:
            st.error("❌ Akses Ditolak! Email atau PIN salah.")
        else:
            st.success("✅ Otorisasi Berhasil! Memuat data dari Sheet `Test Leader`.")
            
            sub_sheet, sub_token = st.tabs(["📊 Rekap Live Sheet `Test Leader`", "🔑 Buka via Token Link WA"])
            
            with sub_sheet:
                if st.button("🔄 Refresh Data Sheet"):
                    st.cache_data.clear()
                
                try:
                    df_hasil = load_data_from_test_leader()
                    if df_hasil.empty:
                        st.info("Sheet `Test Leader` masih kosong.")
                    else:
                        st.markdown("### 🏆 Perbandingan Nilai 35 Soal Calon Leader")
                        kolom_utama = [
                            "Timestamp", "Nama Kandidat", "Tim / Area", 
                            "Total Skor (Max 175)", "Status Rekomendasi",
                            "Skor Kepemimpinan (25)", "Skor Teknis (25)", 
                            "Skor Sudut Pandang (25)", "Skor Problem Solving (25)",
                            "Skor Kehidupan & Profesional (50)", "Skor Integritas & Ketegasan (25)"
                        ]
                        kolom_tersedia = [c for c in kolom_utama if c in df_hasil.columns]
                        st.dataframe(df_hasil[kolom_tersedia], use_container_width=True, hide_index=True)
                        
                        with st.expander("📋 Lihat Rincian Jawaban Soal 1 s/d 35"):
                            st.dataframe(df_hasil.drop(columns=["Token Evaluasi"], errors="ignore"), use_container_width=True)
                            
                except Exception as e:
                    st.error(f"Gagal memuat Sheet: {e}")
            
            with sub_token:
                token_input = st.text_area("Kode Token Evaluasi:", value=incoming_token, height=90)
                if st.button("🔓 Buka Detail dari Token"):
                    res = decrypt_payload(token_input.strip(), input_email_eval)
                    if res:
                        st.metric("Total Skor Akhir", f"{res['total']} / 175", res["status"])
                        st.json(res)
                    else:
                        st.error("Token tidak valid.")
