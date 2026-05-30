# IT Access - Kiosk Mode

## Cara Keluar dari Kiosk Mode (untuk IT Staff)

Saat workstation dalam lock screen (kiosk mode), IT staff dapat keluar ke desktop dengan cara:

1. Tekan kombinasi keyboard: **Ctrl + Shift + Escape**
2. Aplikasi akan langsung tertutup dan desktop akan terlihat

**PERINGATAN:** Kombinasi ini tidak memerlukan password, jadi jangan beritahu ke user biasa.

## Mengganti Kombinasi Tombol

Edit file: `workstation/main.py`

Cari baris:
```python
if key == Qt.Key.Key_Escape and (mods & ctrl_shift) == ctrl_shift:
```

Ganti `Qt.Key.Key_Escape` dengan key lain, misalnya:
- `Qt.Key.Key_F12` untuk F12
- `Qt.Key.Key_F11` untuk F11
- dll

## Menjalankan Kembali Kiosk Mode

Setelah keluar dari kiosk mode, untuk menjalankan kembali:
- Double-click `START-WORKSTATION.bat`
- Atau restart PC (jika sudah setup startup otomatis)

