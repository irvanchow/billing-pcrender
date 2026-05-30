# Panduan Konfigurasi — IDB Bali PC Rental System

## Topologi Jaringan

```
[PC Server / Operator]  ──── LAN ────  [PC Render 1]
  IP: 192.168.1.10                       IP: 192.168.1.11
  Port: 8765                             PC_ID = 1

                         ──── LAN ────  [PC Render 2]
                                         IP: 192.168.1.12
                                         PC_ID = 2
```

---

## A. Konfigurasi PC Server (Operator/Resepsionis)

File konfigurasi: `C:\Program Files\IDB-Rental-Server\config.ini`

```ini
[server]
HOST     = 0.0.0.0
PORT     = 8765
API_KEY  = GANTI_DENGAN_KUNCI_RAHASIA_ANDA
DB_NAME  = rental.db
```

| Parameter | Keterangan |
|-----------|------------|
| `HOST` | `0.0.0.0` agar bisa diakses dari PC Render di jaringan LAN |
| `PORT` | Port API server, default `8765` |
| `API_KEY` | Kunci rahasia — **harus sama persis** dengan yang ada di semua PC Render |
| `DB_NAME` | Nama file database SQLite |

**Langkah setelah edit config:**
1. Simpan file
2. Restart `RentalServer.exe` (klik kanan ikon tray → Exit, lalu buka lagi)

---

## B. Konfigurasi PC Render (Workstation)

File konfigurasi: `C:\Program Files\IDB-Kiosk\config.ini`

```ini
[workstation]
SERVER_URL    = http://192.168.1.10:8765
API_KEY       = GANTI_DENGAN_KUNCI_RAHASIA_ANDA
PC_ID         = 1
POLL_INTERVAL = 5
```

| Parameter | Keterangan |
|-----------|------------|
| `SERVER_URL` | IP dan port PC Server — sesuaikan dengan IP aktual PC Server |
| `API_KEY` | **Harus identik** dengan `API_KEY` di PC Server |
| `PC_ID` | Nomor unik PC ini — PC Render 1 = `1`, PC Render 2 = `2` |
| `POLL_INTERVAL` | Interval polling ke server (detik), default `5` |

**Langkah setelah edit config:**
1. Simpan file
2. Restart `KioskTimer.exe`

---

## C. Poin Penting

- `API_KEY` di server dan **semua** workstation harus **sama persis** (huruf besar/kecil berpengaruh)
- `PC_ID` setiap workstation harus **berbeda** dan sesuai dengan yang terdaftar di server
- Pastikan PC Server menggunakan **IP static** agar `SERVER_URL` di workstation tidak berubah

---

## D. Verifikasi Koneksi

Dari PC Render, buka CMD dan jalankan:

```cmd
ping 192.168.1.10
```

Jika reply → koneksi jaringan OK.

Untuk cek API server, buka browser di PC Render dan akses:

```
http://192.168.1.10:8765/docs
```

Jika muncul halaman dokumentasi API → server berjalan normal.

---

## E. Troubleshooting

| Gejala | Kemungkinan Penyebab | Solusi |
|--------|----------------------|--------|
| PIN selalu ditolak | `API_KEY` tidak sama | Samakan `API_KEY` di kedua config |
| PIN selalu ditolak | `SERVER_URL` salah | Cek IP server, pastikan bisa di-ping |
| Workstation tidak muncul di dashboard | `PC_ID` salah | Sesuaikan `PC_ID` dengan yang terdaftar |
| Tidak bisa terhubung ke server | Firewall memblokir port 8765 | Tambahkan exception di Windows Firewall |
| Server tidak bisa diakses dari luar | `HOST` bukan `0.0.0.0` | Pastikan `HOST = 0.0.0.0` di config server |
