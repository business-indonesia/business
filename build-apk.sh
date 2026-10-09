#!/usr/bin/env bash
# ==============================================================================
# Generated App - Real 1-Click Native Android APK & AAB Builder
# ==============================================================================
set -e

URL="${1:-https://example.com}"
NAME="${2:-Example App}"
PACKAGE="${3:-com.example.app}"
VERSION="${4:-1.0.0}"
VERSION_CODE="${5:-1}"
ICON="${6:-}"

echo "=================================================="
echo "  Generated App - Android Native Builder"
echo "=================================================="
echo "Target URL   : $URL"
echo "App Name     : $NAME"
echo "Package Name : $PACKAGE"
echo "Version      : $VERSION ($VERSION_CODE)"
if [ -n "$ICON" ] && [ -f "$ICON" ]; then
    echo "App Icon     : $ICON"
fi
echo "=================================================="

# Check Java
if ! command -v java >/dev/null 2>&1; then
    echo "[!] ERROR: Java (JDK 17) tidak ditemukan."
    echo "    Silakan install OpenJDK 17 terlebih dahulu:"
    echo "    - Ubuntu/Debian : sudo apt install openjdk-17-jdk"
    echo "    - macOS         : brew install openjdk@17"
    exit 1
fi

DIR="$(cd "$(dirname "$0")" && pwd)"
BUILD_DIR="/tmp/generated-app/build-$$"
mkdir -p "$BUILD_DIR"
mkdir -p "$DIR/generated"

echo "[*] Menyiapkan template Android di $BUILD_DIR..."
cp -R "$DIR/android-template/." "$BUILD_DIR/"

# Injeksi parameter
CLEAN_NAME=$(echo "$NAME" | tr -cd '[:alnum:]_-' | tr ' ' '-')
[ -z "$CLEAN_NAME" ] && CLEAN_NAME="Generated-App"

sed -i.bak "s/{{PACKAGE_NAME}}/$PACKAGE/g" "$BUILD_DIR/app/build.gradle"
sed -i.bak "s/{{VERSION_CODE}}/$VERSION_CODE/g" "$BUILD_DIR/app/build.gradle"
sed -i.bak "s/{{VERSION_NAME}}/$VERSION/g" "$BUILD_DIR/app/build.gradle"
sed -i.bak "s/{{PACKAGE_NAME}}/$PACKAGE/g" "$BUILD_DIR/app/src/main/AndroidManifest.xml" 2>/dev/null || true
sed -i.bak "s|{{APP_NAME}}|$NAME|g" "$BUILD_DIR/app/src/main/res/values/strings.xml"
sed -i.bak "s|{{TARGET_URL}}|$URL|g" "$BUILD_DIR/app/src/main/res/values/strings.xml"

# MainActivity
sed -i.bak "s/{{PACKAGE_NAME}}/$PACKAGE/g" "$BUILD_DIR/app/src/main/java/com/template/app/MainActivity.java"
PKG_PATH=$(echo "$PACKAGE" | tr '.' '/')
mkdir -p "$BUILD_DIR/app/src/main/java/$PKG_PATH"
mv "$BUILD_DIR/app/src/main/java/com/template/app/MainActivity.java" "$BUILD_DIR/app/src/main/java/$PKG_PATH/MainActivity.java"

# Injeksi Icon jika ada
if [ -n "$ICON" ] && [ -f "$ICON" ]; then
    echo "[*] Menyinkronkan App Icon kustom..."
    for d in mipmap-mdpi mipmap-hdpi mipmap-xhdpi mipmap-xxhdpi mipmap-xxxhdpi; do
        cp "$ICON" "$BUILD_DIR/app/src/main/res/$d/ic_launcher.png"
        cp "$ICON" "$BUILD_DIR/app/src/main/res/$d/ic_launcher_round.png"
    done
fi

# Keystore
if command -v keytool >/dev/null 2>&1; then
    echo "[*] Membuat release signing keystore..."
    keytool -genkeypair -v \
        -keystore "$BUILD_DIR/app/release.keystore" \
        -alias release_key \
        -keyalg RSA \
        -keysize 2048 \
        -validity 10000 \
        -storepass android_release_pass \
        -keypass android_release_pass \
        -dname "CN=GeneratedApp, OU=Mobile, O=Business, L=Jakarta, ST=DKI, C=ID" >/dev/null 2>&1 || true
fi

echo "[*] Mengompilasi APK dan AAB dengan Gradle..."
chmod +x "$BUILD_DIR/gradlew"
cd "$BUILD_DIR"
./gradlew assembleRelease bundleRelease --no-daemon

# Copy hasil
echo "[*] Menyimpan hasil build ke $DIR/generated/..."
cp "$BUILD_DIR/app/build/outputs/apk/release/app-release.apk" "$DIR/generated/$CLEAN_NAME.apk"
cp "$BUILD_DIR/app/build/outputs/bundle/release/app-release.aab" "$DIR/generated/$CLEAN_NAME.aab"

# Cleanup
rm -rf "$BUILD_DIR"

echo "=================================================="
echo "  BUILD SUKSES!"
echo "  ✓ APK : $DIR/generated/$CLEAN_NAME.apk"
echo "  ✓ AAB : $DIR/generated/$CLEAN_NAME.aab"
echo "=================================================="
