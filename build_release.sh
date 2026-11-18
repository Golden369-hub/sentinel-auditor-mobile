#!/bin/bash
set -e
echo "[-] Syncing Capacitor assets..."
npx cap copy

echo "[-] Compiling release bundle via PRoot..."
proot-distro login ubuntu -- bash -c '
set -e
cd /data/data/com.termux/files/home/grd_mobile/android
./gradlew bundleRelease
'

echo "[-] Signing release bundle with grd-release-key.jks..."
jarsigner -sigalg SHA256withRSA -digestalg SHA-256 -keystore ~/grd_mobile/grd-release-key.jks ~/grd_mobile/android/app/build/outputs/bundle/release/app-release.aab grd-sentinel-key

echo "[-] Copying signed bundle to /sdcard/Download/..."
cp ~/grd_mobile/android/app/build/outputs/bundle/release/app-release.aab /sdcard/Download/Sentinel-Network-Auditor.aab
cp ~/grd_mobile/grd-release-key.jks /sdcard/Download/grd-release-key.jks

echo "[✓] BUILD, SIGN, AND EXPORT COMPLETE"
ls -lh /sdcard/Download/Sentinel-Network-Auditor.aab
