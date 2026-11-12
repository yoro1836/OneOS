#!/usr/bin/env python3
"""patches/guest_auto_brightness.py and the lux curve guest_prepare.sh writes."""
import re
import subprocess
import sys
import tempfile
import unittest
import xml.dom.minidom
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATCHER = ROOT / 'switcher/patches/guest_auto_brightness.py'
DDC = 'Lcom/android/server/display/DisplayDeviceConfig;'
AUTO = 'Lcom/android/server/display/config/AutoBrightness;'
REL = 'smali_classes2/com/android/server/display/DisplayDeviceConfig.smali'
USER = 'smali_classes2/com/android/server/display/config/DisplayBrightnessMappingConfig.smali'

DDC_TEXT = f'''.class public {DDC}
.super Ljava/lang/Object;

.method public final loadEnableAutoBrightness({AUTO})V
    .locals 2

    const/4 v0, 0x1

    iput-boolean v0, p0, {DDC}->mDdcAutoBrightnessAvailable:Z

    if-eqz p1, :cond_b

    invoke-virtual {{p1}}, {AUTO}->getEnabled()Z

    move-result p1

    iput-boolean p1, p0, {DDC}->mDdcAutoBrightnessAvailable:Z

    :cond_b
    const v1, 0x1110046

    invoke-virtual {{p1, v1}}, Landroid/content/res/Resources;->getBoolean(I)Z

    move-result p1

    iput-boolean p1, p0, {DDC}->mAutoBrightnessAvailable:Z

    return-void
.end method
'''
USER_TEXT = f'''.class public Lcom/android/server/display/config/DisplayBrightnessMappingConfig;
.method public constructor <init>({AUTO})V
    invoke-virtual {{p1}}, {AUTO}->getLuxToBrightnessMapping()Ljava/util/List;
    invoke-interface {{p1}}, Ljava/util/List;->size()I
.end method
'''


def run(root):
    return subprocess.run([sys.executable, '-I', str(PATCHER), str(root)], capture_output=True, text=True)


class PatcherTest(unittest.TestCase):
    def tree(self, ddc=DDC_TEXT, user=USER_TEXT):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        for rel, text in ((REL, ddc), (USER, user)):
            (root / rel).parent.mkdir(parents=True, exist_ok=True)
            (root / rel).write_text(text)
        return root

    def test_a_config_with_a_lux_curve_counts_without_the_resource(self):
        root = self.tree()
        done = run(root)
        self.assertEqual((done.returncode, done.stdout.split()), (0, ['smali_classes2']), done.stderr)
        got = [l.strip() for l in (root / REL).read_text().split('\n') if l.strip() and l.strip()[0] != '#']
        at = got.index('.locals 2')
        self.assertEqual(got[at + 1:at + 14], [
            'if-eqz p1, :oneos_ab_framework',
            f'invoke-virtual {{p1}}, {AUTO}->getEnabled()Z', 'move-result v0',
            'if-eqz v0, :oneos_ab_framework',
            f'invoke-virtual {{p1}}, {AUTO}->getLuxToBrightnessMapping()Ljava/util/List;', 'move-result-object v0',
            'if-eqz v0, :oneos_ab_framework',
            'invoke-interface {v0}, Ljava/util/List;->size()I', 'move-result v0',
            'if-lez v0, :oneos_ab_framework',
            'const/4 v0, 0x1',
            f'iput-boolean v0, p0, {DDC}->mDdcAutoBrightnessAvailable:Z',
            f'iput-boolean v0, p0, {DDC}->mAutoBrightnessAvailable:Z',
        ])
        self.assertEqual(got[at + 14:at + 17], ['return-void', ':oneos_ab_framework', 'const/4 v0, 0x1'])

    def test_a_second_run_and_other_shapes_change_nothing(self):
        root = self.tree()
        run(root)
        before = (root / REL).read_text()
        done = run(root)
        self.assertEqual((done.returncode, done.stdout, (root / REL).read_text()), (0, '', before))
        for name, kw in {'no reader of the map in the dex': dict(user='.class x\n'),
                         'another method': dict(ddc=DDC_TEXT.replace('loadEnableAutoBrightness', 'other')),
                         'no resource': dict(ddc=DDC_TEXT.replace('getBoolean(I)Z', 'getInteger(I)I'))}.items():
            with self.subTest(name):
                root = self.tree(**kw)
                before = (root / REL).read_text()
                done = run(root)
                self.assertEqual((done.returncode, done.stdout, (root / REL).read_text()), (0, '', before))

    def test_the_overlay_build_runs_it(self):
        text = (ROOT / 'scripts/make-overlays.sh').read_text()
        self.assertEqual(text.count('patches/guest_auto_brightness.py" "$WORK/services")"\n'), 1)


class CurveTest(unittest.TestCase):
    def xml(self, *args):
        text = (ROOT / 'switcher/assets/guest_prepare.sh').read_text()
        fn = re.search(r'(?ms)^ddc_xml\(\) \{$.*?^\}$', text).group(0)
        done = subprocess.run(['sh', '-c', fn + '\nddc_xml "$@"', 'sh', *args], capture_output=True, text=True)
        self.assertEqual(done.returncode, 0, done.stderr)
        return done.stdout

    def test_without_auto_there_is_no_curve(self):
        out = self.xml('wide', '4.0')
        self.assertNotIn('autoBrightness', out)
        xml.dom.minidom.parseString(out)

    def test_the_lux_curve_rises_inside_the_panels_floats(self):
        for m in ('', '2.4', '4.0', '5.2980394'):
            with self.subTest(m=m):
                doc = xml.dom.minidom.parseString(self.xml('wide', m, 'auto'))
                auto = doc.getElementsByTagName('autoBrightness')
                self.assertEqual(len(auto), 1)
                self.assertEqual(auto[0].getAttribute('enabled'), 'true')
                pts = [(float(p.getElementsByTagName('first')[0].firstChild.data),
                        float(p.getElementsByTagName('second')[0].firstChild.data))
                       for p in auto[0].getElementsByTagName('point')]
                self.assertEqual(pts[0][0], 0.0)
                self.assertTrue(all(a[0] < b[0] and a[1] < b[1] for a, b in zip(pts, pts[1:])), pts)
                values = [float(v.firstChild.data) for v in doc.getElementsByTagName('value')]
                self.assertGreaterEqual(pts[0][1], min(values))
                self.assertLess(pts[-1][1], 1.0)
                # The map closes before the curve, the curve before the proximity sensor.
                names = [n.nodeName for n in doc.documentElement.childNodes if n.nodeType == n.ELEMENT_NODE]
                self.assertEqual(names, ['screenBrightnessMap', 'autoBrightness', 'proxSensor'])

    def test_the_activator_shows_the_switch_only_with_the_curve(self):
        text = (ROOT / 'switcher/assets/oneos_switch.sh').read_text()
        self.assertIn('--name OneOSAutoBrightness android:bool/config_automatic_brightness_available 0x12 0xffffffff', text)
        self.assertIn('gxo disable --user 0 com.android.shell:OneOSAutoBrightness', text)
        prep = (ROOT / 'switcher/assets/guest_prepare.sh').read_text()
        self.assertIn('rm -f "$STAGE/data/oneos_auto_brightness"', prep)
        self.assertIn('touch "$STAGE/data/oneos_auto_brightness"', prep)


if __name__ == '__main__':
    unittest.main()
