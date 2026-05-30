# Panduan Deployment — IDB Bali PC Rental System

## Arsitektur Jaringan

```
[PC Operator/Resepsionis]  ──── LAN ────  [PC Render 1]
  IP: 192.168.1.10                         IP: 192.168.1.11
  Port: 8765                               Kiosk App

                            ──── LAN ────  [PC Render 2]
                                           IP: 192.168.1.12
                                           Kiosk App
```

---

## LANGKAH 1: Siapkan Build (di PC Development)

**Prasyarat:**
- Python 3.11+ terinstall
- Jalankan `build-all.bat` sebagai Administrator

```
deploy\build-all.bat
```

Output:
- `dist\server\RentalServer\` — folder untuk PC Operator
- `dist\workstation\KioskTimer.exe` — executable untuk PC Render

---

## LANGKAH 2: Setup PC Operator (Resepsionis)

### A. Atur IP Static
1. Buka **Settings > Network & Internet > Ethernet > IP settings**
2. Set IP Manual: `192.168.1.10`, Subnet: `255.255.255.0`, Gateway: `192.168.1.1`

### B. Jalankan Installer
1. Salin folder `dist\server\RentalServer\` ke flashdisk
2. Salin `deploy\server-install.bat` ke flashdisk yang sama
3. Di PC Operator, jalankan `server-install.bat` sebagai **Administrator**

### C. Edit Konfigurasi
Buka `C:\Program Files\IDB-Rental-Server\config.ini`:
```ini
[server]
HOST = 0.0.0.0
PORT = 8765
API_KEY = KUNCI_RAHASIA_ANDA_DISINI
DB_NAME = rental.db
```

> **Penting:** Ganti `API_KEY` dengan string acak yang kuat. Catat karena dipakai di semua PC Render.

### D. Jalankan Aplikasi
Double-click `RentalServer.exe` — muncul sebagai ikon di system tray.

---

## LANGKAH 3: Setup PC Render (Ulangi untuk PC-1 dan PC-2)

### A. Buat Akun Kiosk
Buka **Command Prompt sebagai Administrator**:
```batch
net user kiosk-user KioskPass2026! /add
net localgroup Users kiosk-user /add
```

### B. Aktifkan Auto-Login
Buka **PowerShell sebagai Administrator**:
```powershell
$reg = "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon"
Set-ItemProperty $reg -Name AutoAdminLogon -Value 1
Set-ItemProperty $reg -Name DefaultUserName -Value "kiosk-user"
Set-ItemProperty $reg -Name DefaultPassword -Value "KioskPass2026!"
```

### C. Disable Task Manager (Group Policy)
1. Tekan `Win+R`, ketik `gpedit.msc`, Enter
2. Navigasi ke:
   `User Configuration > Administrative Templates > System > Ctrl+Alt+Del Options`
3. Double-click **Remove Task Manager** → pilih **Enabled** → OK
4. Terapkan ke akun `kiosk-user` dengan **Loopback Policy Processing** jika diperlukan

### D. Jalankan Installer Kiosk
1. Salin `KioskTimer.exe` dan `workstation-install.bat` ke PC Render
2. Jalankan `workstation-install.bat` sebagai **Administrator**
3. Ikuti prompt: masukkan nomor PC (1 atau 2), IP server, dan API Key

### E. Verifikasi Konfigurasi
Cek file `C:\Program Files\IDB-Kiosk\config.ini`:
```ini
[workstation]
SERVER_URL = http://192.168.1.10:8765
API_KEY = KUNCI_RAHASIA_ANDA_DISINI
PC_ID = 1
POLL_INTERVAL = 5
```

### F. Reboot
PC akan boot otomatis ke akun `kiosk-user` dan layar kiosk akan muncul.

---

## Troubleshooting

### Kiosk tidak muncul saat boot
- Cek shortcut di `C:\ProgramData\Microsoft\Windows\Start Menu\Programs\StartUp\`
- Pastikan autologin sudah dikonfigurasi dengan benar
- Jalankan `KioskTimer.exe` manual untuk melihat error

### PIN selalu ditolak
- Pastikan `API_KEY` di server dan workstation **identik**
- Pastikan IP server di `config.ini` workstation benar
- Cek koneksi LAN: `ping 192.168.1.10` dari PC Render
- Buka `http://192.168.1.10:8765/docs` dari browser untuk cek API server

### Server tidak bisa diakses dari PC Render
- Pastikan Windows Firewall mengizinkan port 8765 (sudah otomatis via install script)
- Pastikan IP PC Operator sudah static
- Matikan VPN jika ada

### Render process terhenti saat timer habis
- Ini tidak seharusnya terjadi — kiosk hanya overlay UI
- Jika terjadi, lapor ke developer karena ada konfigurasi power management yang mengganggu

---

## Backup Data

Database tersimpan di:
```
C:\Program Files\IDB-Rental-Server\data\rental.db
```

Backup cukup dengan menyalin file `.db` tersebut. Disarankan backup harian otomatis via Windows Task Scheduler.

---

## Informasi Kontak Developer
Untuk masalah teknis, hubungi tim IT kampus atau developer aplikasi.
