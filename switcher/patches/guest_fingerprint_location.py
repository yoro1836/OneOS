"""Where the phone's under-display fingerprint sensor is, for a guest's lock screen.

Samsung's IFingerprint HAL names the sensor's type (under display, ultrasonic)
but leaves its place empty: One UI reads that elsewhere. A Pixel guest on the
S24 (log 074cef7e) had udfpsBounds=Rect(0, 0 - 0, 0): no fingerprint icon, and
a lock screen laid out around a sensor at the top left corner.

FingerprintProvider.getWorkaroundSensorProps() returns the places that stand in
for the HAL's (AOSP's own workaround list, from a resource). When that list is
empty, add the one guest_props.sh worked out from the phone's own figures:
ro.oneos.udfps_location = "x,y,radius" in panel pixels. No property, or one of
another form: nothing changes.

Usage: guest_fingerprint_location.py <smali root dir>
Prints the smali_* directory (dex file) it changed.
"""
import os
import re
import sys

REL = os.path.join("com", "android", "server", "biometrics", "sensors", "fingerprint", "aidl", "FingerprintProvider.smali")
HEADER = re.compile(r"^\.method (?:public |private |final )*getWorkaroundSensorProps\(Landroid/content/Context;\)Ljava/util/List;$")
LOC = "Landroid/hardware/biometrics/SensorLocationInternal;"
MARK = "# OneOS: the sensor's place, when the HAL gives none"


def piece(i):
    return [f"    const/4 v{i + 2}, 0x{i:x}", "",
            f"    aget-object v{i + 2}, v1, v{i + 2}", "",
            f"    invoke-virtual {{v{i + 2}}}, Ljava/lang/String;->trim()Ljava/lang/String;", "",
            f"    move-result-object v{i + 2}", "",
            f"    invoke-static {{v{i + 2}}}, Ljava/lang/Integer;->parseInt(Ljava/lang/String;)I", "",
            f"    move-result v{i + 2}", ""]


BODY = [
    f"    {MARK}.",
    "    :oneos_loc_start",
    "    invoke-interface {v0}, Ljava/util/List;->isEmpty()Z", "",
    "    move-result v1", "",
    "    if-eqz v1, :oneos_loc_done", "",
    '    const-string v1, "ro.oneos.udfps_location"', "",
    "    invoke-static {v1}, Landroid/os/SystemProperties;->get(Ljava/lang/String;)Ljava/lang/String;", "",
    "    move-result-object v1", "",
    '    const-string v2, ","', "",
    "    invoke-virtual {v1, v2}, Ljava/lang/String;->split(Ljava/lang/String;)[Ljava/lang/String;", "",
    "    move-result-object v1", "",
    "    array-length v2, v1", "",
    "    const/4 v3, 0x3", "",
    "    if-ne v2, v3, :oneos_loc_done", "",
    *piece(0), *piece(1), *piece(2),
    f"    new-instance v5, {LOC}", "",
    '    const-string v6, ""', "",
    f"    invoke-direct {{v5, v6, v2, v3, v4}}, {LOC}-><init>(Ljava/lang/String;III)V", "",
    "    invoke-interface {v0, v5}, Ljava/util/List;->add(Ljava/lang/Object;)Z",
    "    :oneos_loc_end",
    "    .catch Ljava/lang/Exception; {:oneos_loc_start .. :oneos_loc_end} :oneos_loc_done", "",
    "    :oneos_loc_done",
]


def main(root):
    hits = [os.path.join(root, d, REL) for d in sorted(os.listdir(root)) if os.path.isfile(os.path.join(root, d, REL))]
    if len(hits) != 1:
        sys.exit(f"expected one FingerprintProvider.smali, found {len(hits)}")
    path = hits[0]
    src = open(path).read()
    if MARK in src:
        sys.exit(f"{path}: already patched")
    lines = src.split("\n")
    heads = [i for i, l in enumerate(lines) if HEADER.match(l)]
    if len(heads) != 1:
        sys.exit(f"{path}: getWorkaroundSensorProps() found {len(heads)} times, expected once")
    i = heads[0]
    end = next(k for k in range(i, len(lines)) if lines[k] == ".end method")
    m = re.match(r"\s*\.locals (\d+)$", lines[i + 1])
    rets = [k for k in range(i, end) if lines[k].strip().startswith("return")]
    method = "\n".join(lines[i:end])
    if (not m or len(rets) != 1 or lines[rets[0]].strip() != "return-object v0" or
            "new-instance v0, Ljava/util/ArrayList;" not in method or
            f"{LOC}-><init>(Ljava/lang/String;III)V" not in src):
        sys.exit(f"{path}: getWorkaroundSensorProps() is not the list in v0 with one return, unexpected build")
    lines[rets[0]:rets[0]] = BODY
    if int(m.group(1)) < 7:
        lines[i + 1] = "    .locals 7"
    open(path, "w").write("\n".join(lines))
    print("FingerprintProvider.getWorkaroundSensorProps: ro.oneos.udfps_location when the list is empty", file=sys.stderr)
    print(os.path.relpath(path, root).split(os.sep)[0])


if __name__ == "__main__":
    main(sys.argv[1])
