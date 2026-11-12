"""The guest uses the phone's fingerprint sensor without changing what it holds.

The container shares Samsung's IFingerprint HAL, and the templates in it are
One UI's. With the guest's FingerprintService running (the
android.hardware.fingerprint feature, guest_prepare.sh) three clients would
change them:

- FingerprintRemovalClient: ISession.removeEnrollments (Settings' delete,
  "remove all" when a lock is cleared, and the cleanup of templates the
  guest's list lacks, which guest_no_biometric_cleanup.py already stops).
  The caller is told "unable to remove".
- FingerprintInvalidationClient: ISession.invalidateAuthenticatorId, which
  would invalidate One UI's fingerprint-bound keystore keys.
- FingerprintEnrollClient: ISession.enroll. It needs a gatekeeper
  HardwareAuthToken the guest's own lock cannot give; refused up front.

Each startHalOperation() now finishes the client as failed without calling the
HAL. Authentication, detection, enumeration and lockout are unchanged.

Usage: guest_fingerprint_readonly.py <smali root dir>
Prints the smali_* directory (dex file) it changed.
"""
import os
import re
import sys

PKG = "com/android/server/biometrics/sensors/fingerprint/aidl"
BASE = "Lcom/android/server/biometrics/sensors/BaseClientMonitor;"
CB = "Lcom/android/server/biometrics/sensors/ClientMonitorCallback;"
CONV = "Lcom/android/server/biometrics/sensors/ClientMonitorCallbackConverter;"
HEADER = re.compile(r"^\.method (?:public |protected |final )*startHalOperation\(\)V$")
MARK = "# OneOS: the sensor's templates are the phone's (One UI's)"


def finish(tag, msg, before=()):
    # {OWNER} is filled in by patch(): R8 code reads mCallback through
    # BaseClientMonitor, other builds through the client class.
    return [
        f"    {MARK}.",
        f'    const-string v0, "{tag}"',
        "",
        f'    const-string v1, "OneOS: {msg}"',
        "",
        "    invoke-static {v0, v1}, Landroid/util/Slog;->w(Ljava/lang/String;Ljava/lang/String;)I",
        "",
        *before,
        "    iget-object v0, p0, {OWNER}->mCallback:" + CB,
        "",
        "    const/4 v1, 0x0",
        "",
        f"    invoke-interface {{v0, p0, v1}}, {CB}->onClientFinished({BASE}Z)V",
        "",
        "    return-void",
        "",
    ]


def patch(path, call, body, locals_=0):
    src = open(path).read()
    if MARK in src:
        sys.exit(f"{path}: already patched")
    lines = src.split("\n")
    heads = [i for i, l in enumerate(lines) if HEADER.match(l)]
    if len(heads) != 1:
        sys.exit(f"{path}: startHalOperation() found {len(heads)} times, expected once")
    i = heads[0]
    end = next(k for k in range(i, len(lines)) if lines[k] == ".end method")
    method = "\n".join(lines[i:end])
    if call not in method:
        sys.exit(f"{path}: startHalOperation() does not make the HAL call {call}, unexpected build")
    owner = re.search(r"(L[\w/$]+;)->mCallback:" + re.escape(CB), method)
    if not owner:
        sys.exit(f"{path}: startHalOperation() does not read mCallback, unexpected build")
    body = [l.replace("{OWNER}", owner.group(1)) for l in body]
    m = re.match(r"\s*\.locals (\d+)$", lines[i + 1])
    if not m or int(m.group(1)) < 2:
        sys.exit(f"{path}: unexpected startHalOperation header")
    if int(m.group(1)) < locals_:
        lines[i + 1] = f"    .locals {locals_}"
    lines[i + 2:i + 2] = [""] + body
    open(path, "w").write("\n".join(lines))


def main(root):
    dirs = [os.path.join(root, d, PKG) for d in sorted(os.listdir(root))
            if os.path.isfile(os.path.join(root, d, PKG, "FingerprintRemovalClient.smali"))]
    if len(dirs) != 1:
        sys.exit(f"expected one {PKG}/FingerprintRemovalClient.smali, found {len(dirs)}")
    d = dirs[0]
    enr = f"L{PKG}/FingerprintEnrollClient;"
    patch(os.path.join(d, "FingerprintRemovalClient.smali"),
          "Landroid/hardware/biometrics/fingerprint/ISession;->removeEnrollments([I)V",
          finish("FingerprintRemovalClient", "nothing is removed from the phone's sensor; remove fingerprints in One UI", [
              # The caller hears "unable to remove" (6): LockSettingsService's
              # "remove all" waits ten seconds for an answer otherwise.
              "    :oneos_try_start",
              f"    invoke-virtual {{p0}}, {BASE}->getListener(){CONV}",
              "", "    move-result-object v0", "",
              f"    invoke-virtual {{p0}}, {BASE}->getSensorId()I",
              "", "    move-result v1", "",
              f"    invoke-virtual {{p0}}, {BASE}->getCookie()I",
              "", "    move-result v2", "",
              "    const/4 v3, 0x6", "", "    const/4 v4, 0x0", "",
              f"    invoke-virtual {{v0, v1, v2, v3, v4}}, {CONV}->onError(IIII)V",
              "    :oneos_try_end",
              "    .catch Ljava/lang/Exception; {:oneos_try_start .. :oneos_try_end} :oneos_told",
              "", "    :oneos_told"]), locals_=5)
    patch(os.path.join(d, "FingerprintInvalidationClient.smali"),
          "Landroid/hardware/biometrics/fingerprint/ISession;->invalidateAuthenticatorId()V",
          finish("FingerprintInvalidationClient", "the phone's authenticator id is not invalidated"))
    patch(os.path.join(d, "FingerprintEnrollClient.smali"),
          f"{enr}->doEnroll()V",
          finish("FingerprintEnrollClient", "no enrolment from the guest; add fingerprints in One UI",
                 ["    const/4 v0, 0x2", "", "    const/4 v1, 0x0", "",
                  f"    invoke-virtual {{p0, v0, v1}}, {enr}->onError(II)V", ""]))
    print("Fingerprint removal, invalidation and enrolment: no HAL call", file=sys.stderr)
    print(os.path.relpath(d, root).split(os.sep)[0])


if __name__ == "__main__":
    main(sys.argv[1])
