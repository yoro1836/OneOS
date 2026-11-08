#!/system/bin/sh
# Clears the ColorOS guest's screen lock (PIN/pattern) from OneOS's staged data.
# Run as root in One UI, after returning from the guest. One UI's own lock is
# not touched: only files under /data/local/tmp/oneos/data change.
D=/data/local/tmp/oneos/data
[ "$(id -u)" = 0 ] || { echo "run as root (su)"; exit 1; }
[ -d "$D/system" ] && [ ! -L "$D" ] || { echo "no guest data at $D"; exit 1; }
if grep -q " $D[ /]\| /data/local/tmp/oneos/rootfs/data " /proc/self/mountinfo; then
    echo "a guest session is still mounted; return to One UI first"; exit 1
fi
rm -f "$D"/system/locksettings.db "$D"/system/locksettings.db-wal "$D"/system/locksettings.db-shm \
      "$D"/system/locksettings.db-journal "$D"/system/gatekeeper.*.key "$D"/system/password.key \
      "$D"/system/gesture.key "$D"/system/gatekeeper.password.key "$D"/system/gatekeeper.pattern.key
rm -rf "$D"/system_de/0/spblob "$D"/system/oneos_gk
echo "guest screen lock cleared; the next guest session starts with no lock"
