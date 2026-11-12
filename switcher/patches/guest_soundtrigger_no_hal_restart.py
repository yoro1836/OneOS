#!/usr/bin/env python3
"""The guest's sound trigger never restarts One UI's audio HAL.

DefaultHalFactory hands the sound-trigger HAL wrappers a "reboot" action that sets
sys.audio.restart.hal=1. The property service is the phone's own: One UI's init
restarts the audio HAL process, which takes the guest's audioserver down, and the
HAL's onrestart starts One UI's audioserver next to it ("media.audio_policy taken",
then the guest's dies within seconds of every start).

guest_soundtrigger_no_reboot.py stopped that for a model the HAL refuses with a
ServiceSpecificException. On the Galaxy S24 (Exynos 2400, Pixel 9 Pro XL guest) Now
Playing still did it by another path: the guest's audioserver restarted from 12 s
after it registered for as long as Now Playing was on (2026-11-12, 5c99fa37; sound
came back when the owner turned Now Playing off). The action itself now only logs,
whatever the reason: that one model or session fails and audio stays up.

Prints the smali_* directory it changed; nothing when the class is not there. Fails
if the class is there but not in the form this was written for.

Usage: guest_soundtrigger_no_hal_restart.py <apktool decoded services.jar dir>
"""
import os
import re
import sys

REL = os.path.join("com", "android", "server", "soundtrigger_middleware", "DefaultHalFactory.smali")
MARK = "OneOSSoundTrigger"
PAT = re.compile(
    r'(?P<i>[ \t]*)const-string (?P<a>v\d+), "sys\.audio\.restart\.hal"\n(?P<m>(?:\s*\.line \d+\n|\s*\n)*)'
    r'[ \t]*const-string (?P<b>v\d+), "1"\n(?P<n>(?:\s*\.line \d+\n|\s*\n)*)'
    r'[ \t]*invoke-static \{(?P=a), (?P=b)\}, Landroid/os/SystemProperties;->set\(Ljava/lang/String;Ljava/lang/String;\)V\n')


def fail(msg):
    sys.exit("guest_soundtrigger_no_hal_restart: " + msg)


def main():
    if len(sys.argv) != 2:
        fail("usage: guest_soundtrigger_no_hal_restart.py <decoded services.jar dir>")
    root = sys.argv[1]
    hits = [d for d in sorted(os.listdir(root)) if d.startswith("smali") and os.path.isfile(os.path.join(root, d, REL))]
    if not hits:
        return
    if len(hits) != 1:
        fail("DefaultHalFactory in %d dex dirs" % len(hits))
    p = os.path.join(root, hits[0], REL)
    t = open(p, encoding="utf-8").read()
    if MARK in t:
        fail("already patched")
    n = len(PAT.findall(t))
    if n < 1 or t.count('"sys.audio.restart.hal"') != n:
        fail("sys.audio.restart.hal is set %d times in the known form, named %d times" % (n, t.count('"sys.audio.restart.hal"')))

    def rep(m):
        i, a, b = m.group("i"), m.group("a"), m.group("b")
        return (f'{i}const-string {a}, "{MARK}"\n\n'
                f'{i}const-string {b}, "sound trigger HAL restart asked for; not done in a guest (the audio HAL is One UI\'s)"\n\n'
                f'{i}invoke-static {{{a}, {b}}}, Landroid/util/Slog;->w(Ljava/lang/String;Ljava/lang/String;)I\n')

    t = PAT.sub(rep, t)
    open(p, "w", encoding="utf-8").write(t)
    print("guest_soundtrigger_no_hal_restart: %s/%s: %d restart action(s) only log" % (hits[0], REL, n), file=sys.stderr)
    print(hits[0])


if __name__ == "__main__":
    main()
