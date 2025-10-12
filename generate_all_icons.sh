#!/bin/bash

# Create directories for icons
mkdir -p ios_icons android_icons web_icons

# iOS App Icon Sizes (required for App Store)
echo "Generating iOS icons..."
convert app_icon_master.png -resize 20x20 ios_icons/icon-20.png
convert app_icon_master.png -resize 29x29 ios_icons/icon-29.png
convert app_icon_master.png -resize 40x40 ios_icons/icon-40.png
convert app_icon_master.png -resize 58x58 ios_icons/icon-58.png
convert app_icon_master.png -resize 60x60 ios_icons/icon-60.png
convert app_icon_master.png -resize 76x76 ios_icons/icon-76.png
convert app_icon_master.png -resize 80x80 ios_icons/icon-80.png
convert app_icon_master.png -resize 87x87 ios_icons/icon-87.png
convert app_icon_master.png -resize 120x120 ios_icons/icon-120.png
convert app_icon_master.png -resize 152x152 ios_icons/icon-152.png
convert app_icon_master.png -resize 167x167 ios_icons/icon-167.png
convert app_icon_master.png -resize 180x180 ios_icons/icon-180.png
convert app_icon_master.png -resize 1024x1024 ios_icons/icon-1024.png

# Android App Icon Sizes (required for Play Store)
echo "Generating Android icons..."
convert app_icon_master.png -resize 48x48 android_icons/mdpi.png
convert app_icon_master.png -resize 72x72 android_icons/hdpi.png
convert app_icon_master.png -resize 96x96 android_icons/xhdpi.png
convert app_icon_master.png -resize 144x144 android_icons/xxhdpi.png
convert app_icon_master.png -resize 192x192 android_icons/xxxhdpi.png
convert app_icon_master.png -resize 512x512 android_icons/playstore.png

# Web Favicons and PWA Icons
echo "Generating web icons..."
convert app_icon_master.png -resize 16x16 web_icons/favicon-16x16.png
convert app_icon_master.png -resize 32x32 web_icons/favicon-32x32.png
convert app_icon_master.png -resize 48x48 web_icons/favicon-48x48.png
convert app_icon_master.png -resize 64x64 web_icons/favicon-64x64.png
convert app_icon_master.png -resize 96x96 web_icons/favicon-96x96.png
convert app_icon_master.png -resize 128x128 web_icons/favicon-128x128.png
convert app_icon_master.png -resize 192x192 web_icons/android-chrome-192x192.png
convert app_icon_master.png -resize 256x256 web_icons/favicon-256x256.png
convert app_icon_master.png -resize 512x512 web_icons/android-chrome-512x512.png

# Apple Touch Icons for web
convert app_icon_master.png -resize 57x57 web_icons/apple-touch-icon-57x57.png
convert app_icon_master.png -resize 60x60 web_icons/apple-touch-icon-60x60.png
convert app_icon_master.png -resize 72x72 web_icons/apple-touch-icon-72x72.png
convert app_icon_master.png -resize 76x76 web_icons/apple-touch-icon-76x76.png
convert app_icon_master.png -resize 114x114 web_icons/apple-touch-icon-114x114.png
convert app_icon_master.png -resize 120x120 web_icons/apple-touch-icon-120x120.png
convert app_icon_master.png -resize 144x144 web_icons/apple-touch-icon-144x144.png
convert app_icon_master.png -resize 152x152 web_icons/apple-touch-icon-152x152.png
convert app_icon_master.png -resize 180x180 web_icons/apple-touch-icon-180x180.png

# Create ICO file for legacy browser support
convert app_icon_master.png -resize 16x16 -resize 32x32 -resize 48x48 -resize 64x64 web_icons/favicon.ico

echo "All icons generated successfully!"