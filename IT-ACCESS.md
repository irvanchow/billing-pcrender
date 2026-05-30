# IT Access - Kiosk Mode

## Cara Keluar dari Kiosk Mode (untuk IT Staff)

Saat workstation dalam lock screen (kiosk mode), IT staff dapat keluar ke desktop dengan cara:

1. Tekan kombinasi keyboard: **Ctrl + Shift + F12**
2. Masukkan password IT: `admin123`
3. Konfirmasi keluar dari kiosk mode
4. Aplikasi akan tertutup dan desktop akan terlihat

## Mengganti Password IT

Edit file: `workstation/app/gui/lock_screen.py`

Cari baris:
```python
IT_PASSWORD = "admin123"
```

Ganti `"admin123"` dengan password yang diinginkan, lalu restart aplikasi.

## Catatan Keamanan

- Password IT di-hardcode di source code, bukan di config file
- Ini untuk mencegah user biasa mengubah password dari config
- Untuk keamanan lebih baik, gunakan hash password (bcrypt/argon2)
- Kombinasi Ctrl+Shift+F12 dipilih karena tidak mudah tertekan tidak sengaja

## Menjalankan Kembali Kiosk Mode

Setelah keluar dari kiosk mode, untuk menjalankan kembali:
- Double-click `START-WORKSTATION.bat`
- Atau restart PC (jika sudah setup startup otomatis)
