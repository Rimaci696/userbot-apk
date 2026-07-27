[app]
title = UserBot
package.name = userbot
package.domain = com.userbot.app
source.dir = .
source.include_exts = py
version = 1.0
requirements = python3,kivy==2.3.0,telethon,gtts,deep-translator,requests,pillow
orientation = portrait
fullscreen = 0

[android]
permissions = INTERNET,FOREGROUND_SERVICE
api = 33
minapi = 24
android.ndk = 25b
p4a.branch = develop

[buildozer]
log_level = 2
warn_on_root = 1
