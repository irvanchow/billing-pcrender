# IT Access - Kiosk Mode

## Cara Keluar dari Kiosk Mode (untuk IT Staff)

Saat workstation dalam lock screen (kiosk mode), IT staff dapat keluar ke desktop dengan cara:

1. Tekan kombinasi keyboard: **Ctrl + Shift + Q**
2. Aplikasi akan langsung tertutup dan desktop akan terlihat

**PERINGATAN:** Kombinasi ini tidak memerlukan password, jadi jangan beritahu ke user biasa.

## Mengganti Kombinasi Tombol

Edit file: `workstation/app/gui/lock_screen.py`

Cari baris:
```python
if event.key() == Qt.Key.Key_Q and (event.modifiers() & ctrl_shift) == ctrl_shift:
```

Ganti `Qt.Key.Key_Q` dengan key lain, misalnya:
- `Qt.Key.Key_X` untuk X
- `Qt.Key.Key_Z` untuk Z
- dll

## Menjalankan Kembali Kiosk Mode

Setelah keluar dari kiosk mode, untuk menjalankan kembali:
- Double-click `START-WORKSTATION.bat`
- Atau restart PC (jika sudah setup startup otomatis)

