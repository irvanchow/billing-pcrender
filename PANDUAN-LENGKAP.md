# Panduan Lengkap - IDB Bali PC Rental Management System

## Daftar Isi
1. [Requirements](#requirements)
2. [Setup PC Server](#setup-pc-server)
3. [Setup PC Workstation](#setup-pc-workstation)
4. [Konfigurasi](#konfigurasi)
5. [Menjalankan Aplikasi](#menjalankan-aplikasi)
6. [IT Access - Keluar dari Kiosk Mode](#it-access)
7. [Troubleshooting](#troubleshooting)

---

## Requirements

### PC Server (Operator/Resepsionis)
- **OS:** Windows 10/11
- **Python:** 3.11 atau lebih baru
- **RAM:** Minimal 4GB
- **Network:** IP Static (contoh: 192.168.1.10)
- **Koneksi:** Terhubung ke jaringan LAN yang sama dengan PC Render

### PC Workstation (PC Render)
- **OS:** Windows 10/11
- **Python:** 3.11 atau lebih baru
- **RAM:** Minimal 8GB (untuk rendering)
- **Network:** Terhubung ke jaringan LAN yang sama dengan PC Server
- **Akun:** Akun Windows khusus untuk kiosk mode (opsional tapi direkomendasikan)

### Software yang Dibutuhkan
- **Python 3.11+** - Download dari [python.org](https://www.python.org/downloads/)
  - ✅ Centang "Add Python to PATH" saat install
- **Git** (opsional) - Untuk clone repository

---

## Setup PC Server

### 1. Install Python
1. Download Python 3.11+ dari [python.org](https://www.python.org/downloads/)
2. Jalankan installer
3. **PENTING:** Centang "Add Python to PATH"
4. Klik "Install Now"
5. Verifikasi instalasi:
   ```cmd
   python --version
   ```

### 2. Download Project
**Opsi A: Menggunakan Git**
```cmd
cd C:\
git clone https://github.com/irvanchow/billing-pcrender.git
cd billing-pcrender
```

**Opsi B: Download ZIP**
1. Download ZIP dari GitHub
2. Extract ke `C:\billing-pcrender\`

### 3. Install Dependencies
```cmd
cd C:\billing-pcrender
pip install -r server\requirements.txt
```

### 4. Konfigurasi IP Static
1. Buka **Settings > Network & Internet > Ethernet**
2. Klik **IP settings > Edit**
3. Pilih **Manual**, aktifkan **IPv4**
4. Isi:
   - IP address: `192.168.1.10`
   - Subnet mask: `255.255.255.0`
   - Gateway: `192.168.1.1` (sesuaikan dengan router Anda)
   - DNS: `8.8.8.8`
5. Klik **Save**

### 5. Konfigurasi Aplikasi
Edit file `C:\billing-pcrender\server\config.ini`:
```ini
[server]
HOST = 0.0.0.0
PORT = 8765
API_KEY = GANTI_DENGAN_KUNCI_RAHASIA_ANDA
DB_NAME = rental.db
```

**PENTING:** Ganti `API_KEY` dengan string acak yang kuat. Catat karena akan dipakai di semua PC Render.

### 6. Setup Startup Otomatis (Opsional)
```cmd
cd C:\billing-pcrender
SETUP-SERVER-STARTUP.bat
```

### 7. Test Aplikasi
```cmd
cd C:\billing-pcrender
python -m server.main
```

Buka browser dan akses: `http://127.0.0.1:8765/docs`

Jika muncul halaman API documentation → Server berhasil jalan!

---

## Setup PC Workstation

### 1. Install Python
Sama seperti di PC Server (lihat langkah di atas)

### 2. Download Project
Sama seperti di PC Server - download atau clone ke `C:\billing-pcrender\`

### 3. Install Dependencies
```cmd
cd C:\billing-pcrender
pip install -r workstation\requirements.txt
```

### 4. Konfigurasi Aplikasi
Edit file `C:\billing-pcrender\workstation\config.ini`:
```ini
[workstation]
SERVER_URL = http://192.168.1.10:8765
API_KEY = GANTI_DENGAN_KUNCI_RAHASIA_ANDA
PC_ID = 1
POLL_INTERVAL = 5
```

**PENTING:**
- `SERVER_URL`: Ganti dengan IP PC Server yang sebenarnya
- `API_KEY`: **HARUS SAMA PERSIS** dengan API_KEY di PC Server
- `PC_ID`: Nomor unik untuk setiap PC (PC-1 = 1, PC-2 = 2, dst)

### 5. Buat Akun Kiosk (Opsional tapi Direkomendasikan)
Buka **Command Prompt sebagai Administrator**:
```cmd
net user kiosk-user KioskPass2026! /add
net localgroup Users kiosk-user /add
```

### 6. Setup Auto-Login (Opsional)
Buka **PowerShell sebagai Administrator**:
```powershell
$reg = "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon"
Set-ItemProperty $reg -Name AutoAdminLogon -Value 1
Set-ItemProperty $reg -Name DefaultUserName -Value "kiosk-user"
Set-ItemProperty $reg -Name DefaultPassword -Value "KioskPass2026!"
```

### 7. Setup Startup Otomatis
```cmd
cd C:\billing-pcrender
SETUP-WORKSTATION-STARTUP.bat
```

### 8. Test Aplikasi
```cmd
cd C:\billing-pcrender
python -m workstation.main
```

Lock screen fullscreen seharusnya muncul.

---

## Konfigurasi

### Verifikasi Koneksi

**Dari PC Render, test koneksi ke Server:**
```cmd
ping 192.168.1.10
```

Jika reply → koneksi OK.

**Dari PC Render, test API Server:**

Buka browser dan akses: `http://192.168.1.10:8765/docs`

Jika muncul halaman API → Server dapat diakses dari jaringan.

### Firewall

Jika API tidak bisa diakses dari PC Render, buka firewall di **PC Server**.

Buka CMD sebagai Administrator di PC Server:
```cmd
netsh advfirewall firewall add rule name="IDB PC Rental Server" dir=in action=allow protocol=TCP localport=8765 profile=any
```

---

## Menjalankan Aplikasi

### PC Server

**Cara 1: Manual (dengan console untuk debug)**
```cmd
cd C:\billing-pcrender
python -m server.main
```

**Cara 2: Tanpa Console (production)**
```cmd
cd C:\billing-pcrender
START-SERVER-HIDDEN.vbs
```
Double-click file VBS ini. Aplikasi jalan di background, ikon muncul di system tray.

**Cara 3: Startup Otomatis**

Jika sudah jalankan `SETUP-SERVER-STARTUP.bat`, aplikasi otomatis jalan saat Windows boot.

### PC Workstation

**Cara 1: Manual (dengan console untuk debug)**
```cmd
cd C:\billing-pcrender
python -m workstation.main
```

**Cara 2: Tanpa Console (production)**
```cmd
cd C:\billing-pcrender
START-WORKSTATION-HIDDEN.vbs
```
Double-click file VBS ini. Lock screen fullscreen langsung muncul.

**Cara 3: Startup Otomatis**

Jika sudah jalankan `SETUP-WORKSTATION-STARTUP.bat`, aplikasi otomatis jalan saat Windows boot.

---

## IT Access

### Keluar dari Kiosk Mode (PC Workstation)

Saat workstation dalam lock screen (kiosk mode), IT staff dapat keluar ke desktop:

**Tekan kombinasi keyboard: Ctrl + Shift + Q**

Aplikasi akan langsung tertutup dan desktop akan terlihat.

**⚠️ PERINGATAN:** Kombinasi ini tidak memerlukan password. Jangan beritahu ke mahasiswa/user biasa!

### Menjalankan Kembali Kiosk Mode

Setelah keluar dari kiosk mode:
- Double-click `START-WORKSTATION-HIDDEN.vbs`
- Atau restart PC (jika sudah setup startup otomatis)

### Mengganti Kombinasi Tombol

Jika ingin mengganti kombinasi key (misalnya ke Ctrl+Shift+X):

1. Edit file: `workstation/app/gui/lock_screen.py`
2. Cari baris:
   ```python
   if event.key() == Qt.Key.Key_Q and (event.modifiers() & ctrl_shift) == ctrl_shift:
   ```
3. Ganti `Qt.Key.Key_Q` dengan key lain:
   - `Qt.Key.Key_X` untuk X
   - `Qt.Key.Key_Z` untuk Z
   - dll
4. Simpan dan restart aplikasi

---

## Troubleshooting

### Server tidak bisa diakses dari PC Render

**Cek 1: Ping Server**
```cmd
ping 192.168.1.10
```
Jika timeout → masalah jaringan (kabel, switch, atau IP salah)

**Cek 2: Server jalan?**

Di PC Server, buka browser: `http://127.0.0.1:8765/docs`

Jika tidak muncul → server belum jalan atau crash

**Cek 3: Firewall**

Di PC Server, buka CMD sebagai Administrator:
```cmd
netsh advfirewall firewall add rule name="IDB PC Rental Server" dir=in action=allow protocol=TCP localport=8765 profile=any
```

**Cek 4: API Key**

Pastikan `API_KEY` di `server/config.ini` dan `workstation/config.ini` **identik** (huruf besar/kecil berpengaruh)

### PIN selalu ditolak

**Penyebab 1: API Key tidak sama**

Bandingkan `API_KEY` di kedua config file. Harus **persis sama**.

**Penyebab 2: Koneksi terputus**

Cek koneksi dengan `ping 192.168.1.10` dari PC Render.

**Penyebab 3: PIN sudah expired**

Generate PIN baru dari aplikasi server dan langsung input di workstation.

### Lock screen tidak hilang setelah input PIN

Restart aplikasi workstation:
```cmd
cd C:\billing-pcrender
python -m workstation.main
```

Jika masih bermasalah, cek console untuk error message.

### Timer tidak countdown

Cek koneksi polling ke server. Di console workstation seharusnya ada log request setiap 5 detik.

Jika tidak ada → masalah koneksi atau server tidak merespon.

### Aplikasi crash saat startup

**Cek dependencies:**
```cmd
cd C:\billing-pcrender
pip install -r server\requirements.txt
pip install -r workstation\requirements.txt
```

**Jalankan dengan console untuk lihat error:**
```cmd
python -m server.main
python -m workstation.main
```

### Ctrl+Shift+Q tidak bekerja

Pastikan aplikasi workstation jalan dari source code (bukan dari build .exe yang lama).

Test dengan console:
```cmd
python -m workstation.main
```

Tekan Ctrl+Shift+Q → aplikasi seharusnya tertutup.

---

## Kontak Support

Untuk masalah teknis atau bug report:
- GitHub Issues: https://github.com/irvanchow/billing-pcrender/issues
- Email: [sesuaikan dengan email support Anda]

---

## Lisensi

[Sesuaikan dengan lisensi project Anda]
