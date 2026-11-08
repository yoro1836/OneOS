"""The guest's own screen lock, on a software gatekeeper of its own.

guest_no_gatekeeper.py keeps the guest off the phone's gatekeeper HAL (One
UI's lock) by refusing every lock change. This patch, applied after it, gives
the guest LockSettingsService a gatekeeper inside its own system_server
(OneOSGateKeeper, guest_own_gatekeeper/OneOSGateKeeper.java: HMAC-SHA256
handles keyed by /data/system/oneos_gk/key in the guest's staged /data), so
ColorOS can set and check a PIN, pattern or password while the phone's
gatekeeper, weaver, vold keys and FRP stay out of reach as before:

1. LockSettingsService.getGateKeeperService() and
   BiometricDeferredQueue.getGatekeeperService() return OneOSGateKeeper.get().
2. setLockCredentialInternal's OneOS refusal is removed (the escrow-token
   path, setLockCredentialWithTokenInternalLocked, stays refused).
3. The enroll calls guest_no_gatekeeper.py dropped in
   SyntheticPasswordManager.createLskfBasedProtector and newSidForUser are put
   back (on OneOSGateKeeper now). The two re-enroll sites stay dropped: this
   gatekeeper never asks to re-enroll.
4. OPPO's extras after a verified credential (ILockSettingsServiceExt
   notifyVoldDecryptAEKey, notifyPasswordDerivation, handlePasswordChanged)
   are dropped: they go to services shared with One UI or missing here.
5. RecoverableKeyStoreManager.lockScreenSecretAvailable/Changed do nothing:
   its platform keys live in the phone's keystore under uid 1000, the same
   namespace and aliases as One UI's system_server, and a lock change would
   regenerate (delete) them.
6. TrustManagerService never tells the phone's keystore the device is locked
   (KeyStoreAuthorization.onDeviceLocked dropped): One UI's keystore must not
   lock its unlocked-device-required keys behind the guest's lock.
7. SyntheticPasswordManager.createSpBlob passes sid 0: a protector key bound
   to this gatekeeper's sid would need an auth token only gatekeeperd gives
   keystore, so the PIN could never unlock it.

Fails closed: every site must match exactly once.

Usage: guest_own_gatekeeper.py <smali root dir with smali_classes2, smali_classes3>
"""
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GKS = "Landroid/service/gatekeeper/IGateKeeperService;"
OWN = "Lcom/android/server/locksettings/OneOSGateKeeper;"


def find(root, rel):
    for d in sorted(os.listdir(root)):
        p = os.path.join(root, d, rel)
        if d.startswith("smali") and os.path.isfile(p):
            return p
    sys.exit(f"missing {rel}")


def sub1(text, pat, rep, what, flags=re.S, want=1):
    new, n = re.subn(pat, rep, text, flags=flags)
    if n != want:
        sys.exit(f"{what}: {n} matches, want {want}")
    print(f"ok: {what}", file=sys.stderr)
    return new


def getter(text, name, what):
    body = (f".method \\1{name}()Landroid/service/gatekeeper/IGateKeeperService;\n"
            f"    .registers 2\n\n"
            f"    invoke-static {{}}, {OWN}->get(){OWN}\n\n"
            f"    move-result-object v0\n\n"
            f"    return-object v0\n"
            f".end method")
    return sub1(text, r"\.method ((?:[a-z-]+ )*)" + name + r"\(\)Landroid/service/gatekeeper/IGateKeeperService;\n.*?\.end method",
                body, what)


def main(root):
    lss_rel = os.path.join("com", "android", "server", "locksettings", "LockSettingsService.smali")
    lss = find(root, lss_rel)
    ls_dir = os.path.dirname(lss)
    shutil.copy(os.path.join(HERE, "guest_own_gatekeeper", "OneOSGateKeeper.smali"), os.path.join(ls_dir, "OneOSGateKeeper.smali"))

    t = open(lss).read()
    t = getter(t, "getGateKeeperService", "LockSettingsService.getGateKeeperService")
    refusal = ("\n    const-string v0, \"LockSettingsService\"\n\n"
               "    const-string v1, \"OneOS: the screen lock is the phone\\'s gatekeeper; not set in the guest\"\n\n"
               "    invoke-static {v0, v1}, Landroid/util/Slog;->w(Ljava/lang/String;Ljava/lang/String;)I\n\n"
               "    const/4 v0, 0x0\n\n    return v0\n")
    t = sub1(t, r"(\.method private setLockCredentialInternal\(Lcom/android/internal/widget/LockscreenCredential;Lcom/android/internal/widget/LockscreenCredential;IZ\)Z\n(?:    \.[a-z]+[^\n]*\n)+)" + re.escape(refusal),
             r"\1", "setLockCredentialInternal refusal removed")
    # OPPO's lock extras after a verified credential (oplus-services): the
    # vold AE key, the password derivation and OPPO's saved SP. They reach
    # services the guest shares with One UI or lacks; never needed here.
    # handlePasswordChanged: after a verify and after a lock change.
    for sig, n in (("notifyVoldDecryptAEKey(I[B[B)V", 1), ("notifyPasswordDerivation(Lcom/android/internal/widget/LockscreenCredential;I)V", 1),
                   ("handlePasswordChanged(Lcom/android/server/locksettings/SyntheticPasswordManager$SyntheticPassword;)V", 2)):
        t = sub1(t, r"    invoke-interface \{[vp0-9, ]+\}, Lcom/android/server/locksettings/ILockSettingsServiceExt;->" + re.escape(sig) + r"\n",
                 "    nop\n", "OPPO ext " + sig.split("(")[0] + " dropped", want=n)
    open(lss, "w").write(t)

    bdq = os.path.join(ls_dir, "BiometricDeferredQueue.smali")
    t = open(bdq).read()
    t = getter(t, "getGatekeeperService", "BiometricDeferredQueue.getGatekeeperService")
    open(bdq, "w").write(t)

    spm = os.path.join(ls_dir, "SyntheticPasswordManager.smali")
    t = open(spm).read()
    # createLskfBasedProtector: enroll(fakeUserId(userId), null, null, gkPassword); v10 = gatekeeper.
    t = sub1(t, r"(invoke-direct \{v1, v13\}, Lcom/android/server/locksettings/SyntheticPasswordManager;->stretchedLskfToGkPassword\(\[B\)\[B\n\n    move-result-object v3\n\n    \.line \d+\n    const/4 v14, 0x0\n\n)    nop\n\n    const/4 v0, 0x0\n",
             r"\1    invoke-interface {v10, v0, v14, v14, v3}, " + GKS + r"->enroll(I[B[B[B)Landroid/service/gatekeeper/GateKeeperResponse;\n\n    move-result-object v0\n",
             "createLskfBasedProtector enroll restored")
    # newSidForUser: enroll(userId, null, null, sp.deriveGkPassword()).
    t = sub1(t, r"(\.method public newSidForUser\(.*?deriveGkPassword\(\)\[B\n\n    move-result-object v0\n\n    const/4 v1, 0x0\n\n)    nop\n\n    const/4 v0, 0x0\n",
             r"\1    invoke-interface {p1, p3, v1, v1, v0}, " + GKS + r"->enroll(I[B[B[B)Landroid/service/gatekeeper/GateKeeperResponse;\n\n    move-result-object v0\n",
             "newSidForUser enroll restored")
    # Protector keys in the (phone's) keystore are not bound to the sid: only
    # the real gatekeeperd hands keystore the auth token that would unlock
    # them, so a sid-bound key could never be used and the PIN would never
    # unlock. The protector secret still comes from the PIN.
    t = sub1(t, r"(\.method private createSpBlob\(Ljava/lang/String;\[B\[BJ\)\[B\n(?:(?!\.end method).)*?)    move-wide v4, p4\n",
             r"\1    const-wide/16 v4, 0x0\n", "createSpBlob key not sid-bound")
    open(spm, "w").write(t)

    rks = os.path.join(ls_dir, "recoverablekeystore", "RecoverableKeyStoreManager.smali")
    t = open(rks).read()
    for m in ("lockScreenSecretAvailable", "lockScreenSecretChanged"):
        t = sub1(t, r"(\.method public " + m + r"\(Lcom/android/internal/widget/LockscreenCredential;I\)V\n).*?\.end method",
                 r"\1    .registers 3\n\n    return-void\n.end method", f"RecoverableKeyStoreManager.{m} emptied")
    open(rks, "w").write(t)

    tms = find(root, os.path.join("com", "android", "server", "trust", "TrustManagerService.smali"))
    t = open(tms).read()
    t = sub1(t, r"    invoke-virtual \{v1, p1, v2, v3\}, Landroid/security/KeyStoreAuthorization;->onDeviceLocked\(I\[JZ\)I\n",
             "    nop\n", "TrustManagerService onDeviceLocked dropped")
    open(tms, "w").write(t)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
