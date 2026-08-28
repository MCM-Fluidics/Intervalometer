[app]
# Build with: buildozer android debug deploy run
title = Night Intervalometer
package.name = nightintervalometer
package.domain = org.intervalometer
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
requirements = python3,kivy
orientation = portrait
fullscreen = 0

[buildozer]
log_level = 2
warn_on_root = 1

[android]
 # A normal Kivy app cannot inject taps into another app. An Android
 # AccessibilityService/overlay companion is required for real camera pushes.
android.api = 35
android.minapi = 23
android.archs = arm64-v8a, armeabi-v7a
android.permissions = WAKE_LOCK, SYSTEM_ALERT_WINDOW
