[app]
title = Neon Surge 2
package.name = neonsurge
package.domain = org.neonsurge
source.dir = .
source.include_exts = py,png,jpg,jpeg,ttf,wav,ogg,mp3,json
source.include_patterns = game/**,main.py,requirements.txt
version = 0.1.0

requirements = python3,pygame,pygame_gui
orientation = landscape
fullscreen = 1

android.permissions = INTERNET
android.archs = arm64-v8a,armeabi-v7a
android.api = 33
android.minapi = 24
android.ndk = 25b
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
