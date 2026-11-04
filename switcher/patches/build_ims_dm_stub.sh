#!/bin/sh
# Build switcher/assets/OneOSImsDmStub.apk: an empty app named com.ims.dm.
# Samsung IMS on a Korean SIM (RegistrationGovernorKor.isOmadmConfigAvailable)
# loads the DM P-CSCF list only once DM config completes or times out, and it
# starts that wait only when the package com.ims.dm exists. One UI's agent is
# android.uid.system and cannot run in the guest; this stub only makes IMS take
# the 30 s timeout path, which reads the DM settings guest_prepare.sh copied.
set -eu
HERE=$(cd "$(dirname "$0")" && pwd); ROOT=$(cd "$HERE/../.." && pwd)
SDK=${ANDROID_HOME:?ANDROID_HOME}
BT=$(ls -d "$SDK"/build-tools/* | sort -V | tail -1)
AJ=$(ls "$SDK"/platforms/*/android.jar | sort -V | tail -1)
WORK=$(mktemp -d); trap 'rm -rf "$WORK"' EXIT
"$BT/aapt2" link --manifest "$HERE/ims_dm_stub/AndroidManifest.xml" -I "$AJ" -o "$WORK/u.apk"
"$BT/zipalign" -f 4 "$WORK/u.apk" "$WORK/a.apk"
KS=${ONEOS_STUB_KEYSTORE:-$HOME/.android/debug.keystore}
[ -f "$KS" ] || keytool -genkeypair -keystore "$KS" -storepass android -keypass android -alias androiddebugkey -dname CN=Android\ Debug -keyalg RSA -validity 10000 >/dev/null
"$BT/apksigner" sign --ks "$KS" --ks-pass pass:android --out "$ROOT/switcher/assets/OneOSImsDmStub.apk" "$WORK/a.apk"
echo "built switcher/assets/OneOSImsDmStub.apk ($(stat -c%s "$ROOT/switcher/assets/OneOSImsDmStub.apk") bytes)"
