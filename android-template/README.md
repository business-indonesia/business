# Android Template Specifications (Phase 01 Architecture)

## Overview
This directory serves as the base native Android project template that will be cloned and configured by the worker in Phase 03.

## Target Android Stack
- **Language**: Kotlin 1.9+
- **Minimum SDK**: 24 (Android 7.0 Nougat)
- **Target SDK / Compile SDK**: 34+ (Android 14)
- **Build System**: Gradle 8.x with Android Gradle Plugin (AGP) 8.x
- **WebView Framework**: Modern Android WebKit WebView with Chrome Custom Tabs fallback
- **Features Planned for Phase 03**:
  - Full-screen webview rendering
  - Pull-to-refresh (SwipeRefreshLayout)
  - JavaScript bridge and interface
  - Geolocation and file upload camera/gallery permissions
  - Push notification hooks (Firebase Cloud Messaging)
  - Splash screen API (androidx.core.splashscreen)
  - Offline fallback screen

## Injection Points
During compilation, the worker dynamically customizes:
1. `app/build.gradle.kts`: `applicationId`, `versionCode`, `versionName`
2. `AndroidManifest.xml`: Permissions, app label, scheme handlers
3. `res/values/strings.xml`: `app_name`, `web_url`
4. `res/values/colors.xml`: `primary_color`, `splash_color`
5. `res/mipmap-*`: Custom app launcher icons
