"""Automatic brightness from the display config the guest is given.

An AOSP framework offers automatic brightness on a display when the resource
config_automatic_brightness_available is true and the display's config does not switch it off
(DisplayDeviceConfig.loadEnableAutoBrightness). The resource comes from the image's own phone's
vendor overlay, which a guest does not have (Pixel on the Galaxy S24, 2026-11-12: no adaptive
brightness). guest_prepare.sh writes the display config for the phone's panel, with a lux curve
of its own; this patch lets such a config answer by itself: an <autoBrightness enabled="true">
element that brings a lux-to-brightness map makes automatic brightness available on that display
whatever the resource says. Every other config goes the framework's way as before. No new
reference: the dex with the display code has no room for one.

Any other framework shape is left alone (a note on stderr, nothing on stdout, exit 0).

Usage: guest_auto_brightness.py <smali root dir>
Prints the smali_* directory it changed.
"""
import os
import re
import sys

REL = os.path.join("com", "android", "server", "display", "DisplayDeviceConfig.smali")
DDC = "Lcom/android/server/display/DisplayDeviceConfig;"
AUTO = "Lcom/android/server/display/config/AutoBrightness;"
MARK = ":oneos_ab_framework"


def hook():
    return f"""\
    # OneOS: a display config that brings its own lux curve makes automatic brightness
    # available by itself (patches/guest_auto_brightness.py); the phone's resource is not
    # asked, the guest has no vendor overlay that sets it.
    if-eqz p1, {MARK}

    invoke-virtual {{p1}}, {AUTO}->getEnabled()Z

    move-result v0

    if-eqz v0, {MARK}

    invoke-virtual {{p1}}, {AUTO}->getLuxToBrightnessMapping()Ljava/util/List;

    move-result-object v0

    if-eqz v0, {MARK}

    invoke-interface {{v0}}, Ljava/util/List;->size()I

    move-result v0

    if-lez v0, {MARK}

    const/4 v0, 0x1

    iput-boolean v0, p0, {DDC}->mDdcAutoBrightnessAvailable:Z

    iput-boolean v0, p0, {DDC}->mAutoBrightnessAvailable:Z

    return-void

    {MARK}""".split("\n")


def main(root):
    dirs = [d for d in sorted(os.listdir(root))
            if d.startswith("smali") and os.path.isfile(os.path.join(root, d, REL))]
    if len(dirs) != 1:
        return f"{len(dirs)} files {REL}"
    path = os.path.join(root, dirs[0], REL)
    with open(path) as f:
        text = f.read()
    if MARK in text:
        return "this services.jar already has it"
    lines = text.split("\n")
    head = re.compile(r"^\.method (?:[a-z]+ )*loadEnableAutoBrightness\(" + re.escape(AUTO) + r"\)V$")
    starts = [i for i, l in enumerate(lines) if head.match(l)]
    if len(starts) != 1 or " static " in lines[starts[0]]:
        return f"loadEnableAutoBrightness found {len(starts)} times"
    i = starts[0]
    end = next(k for k in range(i, len(lines)) if lines[k] == ".end method")
    body = "\n".join(lines[i:end])
    m = re.fullmatch(r"\s*\.locals (\d+)", lines[i + 1])
    if not m or int(m.group(1)) < 1:
        return "loadEnableAutoBrightness has no free register"
    for needs in ("->mDdcAutoBrightnessAvailable:Z", "->mAutoBrightnessAvailable:Z",
                  "Landroid/content/res/Resources;->getBoolean(I)Z"):
        if needs not in body:
            return f"loadEnableAutoBrightness does not use {needs}"
    # The same dex already calls what the hook calls (DisplayBrightnessMappingConfig reads the map).
    user = os.path.join(root, dirs[0], os.path.dirname(REL), "config", "DisplayBrightnessMappingConfig.smali")
    used = open(user).read() if os.path.isfile(user) else ""
    for needs in (AUTO + "->getLuxToBrightnessMapping()Ljava/util/List;", "Ljava/util/List;->size()I"):
        if needs not in used:
            return f"the display code's dex does not use {needs}"
    if AUTO + "->getEnabled()Z" not in body:
        return "loadEnableAutoBrightness does not ask the config"
    at = i + 2
    while lines[at].strip() == "" or lines[at].strip().startswith((".param", ".annotation", ".end")):
        at += 1
    lines[at:at] = hook() + [""]
    with open(path, "w") as f:
        f.write("\n".join(lines))
    print(dirs[0])
    return "DisplayDeviceConfig.loadEnableAutoBrightness"


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__.strip().split("\n")[-2])
    print("guest_auto_brightness: " + main(sys.argv[1]), file=sys.stderr)
