|F:\kaifa\pythons\rj\Android\buildozer.spec
[app]
title = 白玉京复习系统
package.name = quiz_system
package.domain = com.baiyujing
source.dir = quiz_app
source.include_exts = py,png,jpg,kv,atlas,json
version = 1.0.1
requirements = python3,kivy,sqlite3
orientation = portrait
fullscreen = 0
android.api = 33
android.minapi = 21
android.ndk = 25b
android.sdk = 30
p4a.bootstrap = sdl2
p4a.port = 8000
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.add_files = ../question_banks
log_level = 2
warn_on_root = 1
