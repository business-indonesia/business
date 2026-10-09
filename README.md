# Generated App

Website URL → Android APK + AAB

**Generated App** adalah aplikasi sederhana, cepat, dan sangat ringan (**Simple — Fast — Lightweight**) untuk mengubah URL website menjadi aplikasi Android WebView native yang menghasilkan:

- **`.apk`** (Release APK resmi siap install pada smartphone Android)
- **`.aab`** (Android App Bundle release resmi siap upload ke Google Play Console)

---

## ⚡ Langsung Pakai `index.html` (Tanpa VPS, Tanpa Python Server)

Website ini **dapat langsung digunakan via `index.html`**:
- **TIDAK PERLU** VPS khusus, Docker, Kubernetes, Redis, atau build server berat.
- **TIDAK PERLU** mengonfigurasi cPanel *Setup Python App*.
- Cukup upload file `index.html` (atau ekstrak file zip) ke direktori web/subdomain (`public_html` di `generated.business.web.id`).
- Halaman langsung terbuka seketika dan berfungsi penuh di browser!

---

## 🛠️ Mengapa Muncul Error "Ada Masalah saat mengurai paket"?

Jika sebuah file `.apk` dibungkus secara sintetis di dalam browser (JavaScript) tanpa melewati compiler resmi Android SDK, kernel Android OS (komponen `PackageParser` & ART runtime) akan **menolaknya saat instalasi** dengan pesan *"Ada Masalah saat mengurai paket"* (Parse Error).

Penyebab teknis sistem operasi Android (terutama Android 10, 11, 12, 13, 14, 15):
1. **Binary XML Resmi**: `AndroidManifest.xml` wajib dikompilasi oleh compiler C++ **`aapt2`** resmi Google dengan pemetaan resource ID framework.
2. **Bytecode Dalvik Riil**: File `classes.dex` wajib dikompilasi oleh compiler **`d8`/`r8`** resmi dari Java bytecode.
3. **Penyelarasan Memori 4-Byte Boundary**: Uncompressed entries wajib diselaraskan via **`zipalign`**.
4. **Tanda Tangan Kriptografi APK Scheme v2/v3**: Android modern menolak APK tanpa blok signature biner v2 (`apksigner`).

---

## 🚀 Solusi: Cloud Build Runner Otomatis (Serverless — Gratis Tanpa VPS)

Aplikasi telah dilengkapi **Serverless Cloud Build Runner** yang terintegrasi langsung di dalam `index.html`:

```text
User Input URL
    ↓
Klik Generate APK + AAB
    ↓
Website memicu Cloud Build Runner (GitHub Actions API)
    ↓
Serverless Runner (Ubuntu + OpenJDK 17 + Android SDK 34 + Gradle)
    ↓
Kompilasi Biner Resmi (aapt2, d8, zipalign, apksigner)
    ↓
✓ Download APK Resmi (100% Berhasil Diinstal di HP Android)
✓ Download AAB Resmi (Siap Upload Google Play Console)
```

### Cara Mengaktifkan Cloud Build Runner (Hanya Butuh 1 Menit, Otomatis Selamanya):
1. Buka website di browser (`https://generated.business.web.id`).
2. Di halaman **Generate App**, klik tombol **⚙️ Pengaturan Cloud**.
3. Masukkan:
   - **Repository GitHub**: `username/generated-app-dan-aab`
   - **GitHub Personal Access Token (PAT)**: Token gratis dari GitHub (buka *github.com → Settings → Developer Settings → Personal access tokens*, beri centang pada `workflow` dan `repo`).
4. Klik **💾 Simpan Pengaturan**.
5. Selesai! Kini setiap kali Anda mengklik **Generate APK + AAB**, sistem akan otomatis mengompilasi APK dan AAB resmi di cloud secara gratis tanpa butuh VPS. Hasil build **100% installable di HP tanpa parse error!**

---

## 💻 Opsi Alternatif: Build Lokal (1-Click Script & Android Studio)

Jika Anda ingin mengompilasi langsung di laptop/komputer Anda:

### 1. 1-Click Script `build-apk.sh` (Mac / Linux)
Jalankan satu perintah di terminal (membutuhkan Java 17):
```bash
chmod +x build-apk.sh
./build-apk.sh "https://example.com" "Nama App" "com.example.app"
```
File APK & AAB resmi langsung tersimpan di folder `generated/`.

### 2. Download Proyek Android (.zip) Siap Kompilasi
Di `index.html`, klik **Download Source (.zip)**. Proyek ini sudah lengkap dengan seluruh konfigurasi Gradle, Activity WebView, icons, dan strings. Buka folder ini di **Android Studio**, lalu pilih menu **Build > Build Bundle(s) / APK(s) > Build APK(s)**.

---

## 📱 Fitur Native Android WebView

- **Pure Android Native WebView (Bukan Hybrid)**:
  - Menggunakan framework Android asli (`android.webkit.WebView` dan `android.app.Activity`).
  - Tanpa framework besar (No Flutter, No React Native, No Ionic, No Cordova). Ukuran biner sangat kecil dan cepat.
- **Dukungan WebView Lengkap**:
  - JavaScript = ON
  - DOM Storage / localStorage = ON
  - Cookies & 3rd-Party Cookies = ON
  - Enforce HTTPS
  - Navigasi Tombol Back Android (`goBack()` jika ada history web / `finish()` jika di halaman awal)
  - Intent external link otomatis (WhatsApp, Telegram, Telepon, Email, SMS, Google Maps)
  - File upload form support via `WebChromeClient`
- **Auto Reverse Domain Package Name**:
  - Mengisi URL `https://sangkala.business.web.id` otomatis membuat package name `id.web.business.sangkala`.

---

## 🔑 Login Default Admin

- **Email**: `admin@example.com`
- **Password**: `admin123456`

---

## 📁 Struktur Project

```text
generated-app-dan-aab/
│
├── index.html                  # File utama! Buka langsung di browser atau cPanel
├── .github/workflows/          # Pipeline Serverless Cloud Runner
│   └── build-android.yml       # Workflow kompilasi resmi Ubuntu + SDK 34 + Gradle
│
├── android-template/           # Template Android native WebView
│   ├── settings.gradle
│   ├── build.gradle
│   ├── gradle.properties
│   ├── gradlew
│   └── app/
│       ├── build.gradle
│       ├── proguard-rules.pro
│       └── src/main/
│           ├── AndroidManifest.xml
│           ├── java/com/template/app/MainActivity.java
│           └── res/
│
├── build-apk.sh                # Skrip kompilasi lokal 1-klik (Mac/Linux)
├── server.py                   # (Opsional) Entry point server Python lokal
├── package.json                # (Opsional) Package metadata
├── README.md                   # Dokumentasi lengkap
│
├── generated-app-dan-aab.zip   # Archive final siap upload (< 120 KB)
└── generated-app-dan-aab.tar.gz# Archive alternatif (< 100 KB)
```
