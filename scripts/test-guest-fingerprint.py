#!/usr/bin/env python3
"""patches/guest_fingerprint_readonly.py and the fingerprint parts of guest_prepare.sh."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATCHER = ROOT / 'switcher/patches/guest_fingerprint_readonly.py'
PKG = 'com/android/server/biometrics/sensors/fingerprint/aidl'
BASE = 'Lcom/android/server/biometrics/sensors/BaseClientMonitor;'
CB = 'Lcom/android/server/biometrics/sensors/ClientMonitorCallback;'
SESSION = 'Landroid/hardware/biometrics/fingerprint/ISession;'


def client(name, call, owner=BASE):
    return f'''.class public L{PKG}/{name};
.super Ljava/lang/Object;

.method public startHalOperation()V
    .locals 3

    :try_start_0
    {call}
    :try_end_f
    .catch Landroid/os/RemoteException; {{:try_start_0 .. :try_end_f}} :catch_10

    return-void

    :catch_10
    move-exception v0

    iget-object v0, p0, {owner}->mCallback:{CB}

    const/4 v1, 0x0

    invoke-interface {{v0, p0, v1}}, {CB}->onClientFinished({BASE}Z)V

    return-void
.end method
'''


CALLS = {
    'FingerprintRemovalClient': f'invoke-interface {{v0, v1}}, {SESSION}->removeEnrollments([I)V',
    'FingerprintInvalidationClient': f'invoke-interface {{v0}}, {SESSION}->invalidateAuthenticatorId()V',
    'FingerprintEnrollClient': f'invoke-virtual {{p0}}, L{PKG}/FingerprintEnrollClient;->doEnroll()V',
}


def tree(tmp, calls=CALLS, owner=BASE):
    d = Path(tmp) / 'smali_classes2' / PKG
    d.mkdir(parents=True)
    for name, call in calls.items():
        (d / f'{name}.smali').write_text(client(name, call, owner))
    return d


def run(tmp):
    return subprocess.run([sys.executable, '-I', str(PATCHER), tmp], capture_output=True, text=True)


def first_return(text):
    body = text.split('.method public startHalOperation()V', 1)[1]
    return body.split('return-void', 1)[0]


class Patcher(unittest.TestCase):
    def test_no_hal_call_before_the_first_return(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = tree(tmp)
            r = run(tmp)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertEqual(r.stdout.strip(), 'smali_classes2')
            for name in CALLS:
                head = first_return((d / f'{name}.smali').read_text())
                self.assertNotIn('ISession;', head)
                self.assertNotIn('doEnroll', head)
                self.assertIn('const/4 v1, 0x0', head)
                self.assertIn(f'{CB}->onClientFinished({BASE}Z)V', head)
            enroll = first_return((d / 'FingerprintEnrollClient.smali').read_text())
            self.assertIn('const/4 v0, 0x2', enroll)
            self.assertIn('FingerprintEnrollClient;->onError(II)V', enroll)

    def test_callback_owner_as_the_build_names_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            own = f'L{PKG}/FingerprintRemovalClient;'
            d = tree(tmp, owner=own)
            self.assertEqual(run(tmp).returncode, 0)
            self.assertIn(f'{own}->mCallback:{CB}', first_return((d / 'FingerprintRemovalClient.smali').read_text()))

    def test_refuses_twice_and_another_shape(self):
        with tempfile.TemporaryDirectory() as tmp:
            tree(tmp)
            self.assertEqual(run(tmp).returncode, 0)
            self.assertNotEqual(run(tmp).returncode, 0)
        with tempfile.TemporaryDirectory() as tmp:
            tree(tmp, dict(CALLS, FingerprintRemovalClient='nop'))
            r = run(tmp)
            self.assertNotEqual(r.returncode, 0)
            self.assertIn('unexpected build', r.stderr)


class Prepare(unittest.TestCase):
    TEXT = (ROOT / 'switcher/assets/guest_prepare.sh').read_text()

    def test_feature_only_with_the_guards(self):
        i = self.TEXT.index('oneos-fingerprint.xml')
        cond = self.TEXT[self.TEXT.rindex('\n    if ', 0, i):i]
        self.assertIn('ONEOS_GUEST_FINGERPRINT:-1', cond)
        self.assertIn('grep -qw fpreadonly', cond)
        self.assertIn('grep -qw biometric', cond)

    def test_list_carried_over(self):
        block = self.TEXT[self.TEXT.index('BIO_DST="$STAGE/data/system/users/0"'):]
        block = block[:block.index('\nfi\n')]
        script = block + '\nfi\n'
        with tempfile.TemporaryDirectory() as tmp:
            t = Path(tmp)
            (t / 'petc/permissions').mkdir(parents=True)
            (t / 'petc/permissions/oneos-fingerprint.xml').write_text('x')
            (t / 'host').mkdir()
            (t / 'host/settings_fingerprint_0.xml').write_text('one ui')
            (t / 'host/settings_face.xml').write_text('face')
            dst = t / 'stage/data/system/users/0'
            dst.mkdir(parents=True)
            (dst / 'settings_fingerprint_7.xml').write_text('stale')
            env = {'STAGE': str(t / 'stage'), 'PETC': str(t / 'petc'), 'BB': 'true',
                   'ONEOS_HOST_USER_DIR': str(t / 'host'), 'PATH': '/usr/bin:/bin'}
            r = subprocess.run(['sh', '-c', script], env=env, capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn('1 list(s)', r.stdout)
            self.assertEqual(sorted(p.name for p in dst.iterdir()), ['settings_fingerprint_0.xml'])
            self.assertEqual((dst / 'settings_fingerprint_0.xml').read_text(), 'one ui')
            (t / 'petc/permissions/oneos-fingerprint.xml').unlink()
            r = subprocess.run(['sh', '-c', script], env=env, capture_output=True, text=True)
            self.assertIn('Guest fingerprint: off', r.stdout)


LOCATION = ROOT / 'switcher/patches/guest_fingerprint_location.py'
PROVIDER = f'''.class public L{PKG}/FingerprintProvider;
.super Ljava/lang/Object;

.method public final getWorkaroundSensorProps(Landroid/content/Context;)Ljava/util/List;
    .locals 5

    new-instance v0, Ljava/util/ArrayList;

    invoke-direct {{v0}}, Ljava/util/ArrayList;-><init>()V

    :cond_32
    return-object v0
.end method

.method public final parseSensorLocation()V
    .locals 7

    invoke-direct {{v1, v3, v4, v5, p1}}, Landroid/hardware/biometrics/SensorLocationInternal;-><init>(Ljava/lang/String;III)V

    return-void
.end method
'''


class Location(unittest.TestCase):
    def test_patcher(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp) / 'smali' / PKG
            d.mkdir(parents=True)
            (d / 'FingerprintProvider.smali').write_text(PROVIDER)
            cmd = [sys.executable, '-I', str(LOCATION), tmp]
            r = subprocess.run(cmd, capture_output=True, text=True)
            self.assertEqual((r.returncode, r.stdout.strip()), (0, 'smali'), r.stderr)
            text = (d / 'FingerprintProvider.smali').read_text()
            method = text.split('.end method')[0]
            self.assertIn('.locals 7', method)
            self.assertIn('"ro.oneos.udfps_location"', method)
            self.assertLess(method.index(':oneos_loc_done'), method.index('return-object v0'))
            self.assertEqual(text.count('return-object v0'), 1)
            self.assertNotEqual(subprocess.run(cmd, capture_output=True).returncode, 0)

    def props(self, position, device='e1s', env=None):
        src = (ROOT / 'switcher/assets/guest_props.sh').read_text()
        a = src.index('    FPP=${ONEOS_FP_POSITION_FILE')
        code = src[a:src.index("    # ColorOS's animation level", a)]
        with tempfile.TemporaryDirectory() as tmp:
            t = Path(tmp)
            (t / 'display_modes_host.log').write_text(
                '    activeMode={id=0, hwcId=4, resolution=1080x2340, vsyncRate=120.00 Hz, dpi=415.64x418.56, group=0, vrrConfig=N/A}\n')
            if position is not None:
                (t / 'pos').write_text(position + '\n')
            (t / 'new').write_text('')
            e = {'STAGE': tmp, 'NEW': str(t / 'new'), 'ONEOS_FP_POSITION_FILE': str(t / 'pos'), 'PATH': '/usr/bin:/bin', **(env or {})}
            subprocess.run(['sh', '-c', f'getprop() {{ echo {device}; }}\n' + code], env=e, check=True, capture_output=True)
            return (t / 'new').read_text()

    def test_s24_position_in_pixels(self):
        self.assertEqual(self.props('30.87,0.00,7.50,8.25,14.80,14.80,13.00,13.00,5.00'), 'ro.oneos.udfps_location=540,1763,106\n')

    def test_left_out(self):
        self.assertEqual(self.props(None), '')
        self.assertEqual(self.props('garbage'), '')
        self.assertEqual(self.props('300.0,0.00,7.50,8.25,14.80,14.80,13.00,13.00,5.00'), '')
        self.assertEqual(self.props('30.87,0.00,7.50,8.25,14.80,14.80,13.00,13.00,5.00', device='pa3q'), '')
        self.assertEqual(self.props('30.87,0.00,7.50,8.25,14.80,14.80,13.00,13.00,5.00', env={'ONEOS_GUEST_FINGERPRINT': '0'}), '')
        self.assertEqual(self.props('30.87,0.00,7.50,8.25,14.80,14.80,13.00,13.00,5.00', env={'ONEOS_GUEST_UDFPS_LOCATION': ''}), '')

    def test_set_by_hand(self):
        self.assertEqual(self.props(None, device='pa3q', env={'ONEOS_GUEST_UDFPS_LOCATION': '720,2500,130'}), 'ro.oneos.udfps_location=720,2500,130\n')


if __name__ == '__main__':
    unittest.main()
