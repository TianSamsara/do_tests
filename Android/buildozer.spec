[app]
title = 刷题系统
package.name = quiz_system
package.domain = com.quiz
source.dir = quiz_app
source.include_exts = py,png,jpg,kv,atlas,json,ttf,ttc
version = 1.0.0
requirements = python3,kivy,sqlite3
orientation = portrait
fullscreen = 0
android.api = 33
android.minapi = 21
android.ndk = 25b
android.sdk = 30
p4a.bootstrap = sdl2
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
log_level = 2
warn_on_root = 1

# Android specific
android.accept_sdk_license = True
android.arch = armeabi-v7a,arm64-v8a
