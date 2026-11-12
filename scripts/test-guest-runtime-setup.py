#!/usr/bin/env python3
"""Run the actual guest-su and file-bind setup snippets in isolated fixtures."""
from pathlib import Path
import os, subprocess, tempfile, unittest, sys
ROOT=Path(__file__).resolve().parents[1]
class SetupTest(unittest.TestCase):
 def test_native_broker_is_copied_without_a_host_su_file(self):
  script=(ROOT/'switcher/assets/guest_prepare.sh').read_text()
  snippet=script.split('Setting up /system/xbin/su (KernelSU Bridge) ==="',1)[1].split('echo "=== 7.',1)[0]
  with tempfile.TemporaryDirectory() as d:
   stage=Path(d); (stage/'data/oneos_root').mkdir(parents=True);(stage/'data/oneos_root/enabled').touch();(stage/'rootfs/system/xbin').mkdir(parents=True)
   broker=stage/'guest_root';broker.write_bytes(b'guest broker fixture')
   bb=stage/'busybox';bb.write_text('#!/bin/sh\n[ "$1" = mount ] && exit 0\nexit 1\n');bb.chmod(0o755)
   subprocess.run(['sh','-c',snippet],env={**os.environ,'STAGE':d,'ROOTFS':str(stage/'rootfs'),'BB':str(bb)},check=True)
   actual=stage/'rootfs/system/xbin/su';self.assertEqual(actual.read_bytes(),broker.read_bytes());self.assertTrue(actual.stat().st_mode & 0o111)
 def test_missing_xbin_is_added_only_to_enabled_guests_overlay(self):
  script=(ROOT/'switcher/assets/guest_prepare.sh').read_text()
  helper=script[script.index('guest_root_mountpoint() {'):script.index('if [ -d "$SAMCAM_SRC" ] && [ $SAMCAM_IMAGE = 0 ]; then')]
  with tempfile.TemporaryDirectory() as d:
   stage=Path(d);(stage/'rootfs/system').mkdir(parents=True);(stage/'data/oneos_root').mkdir(parents=True);up=stage/'overlay';up.mkdir()
   env={**os.environ,'STAGE':d,'ROOTFS':str(stage/'rootfs')}
   subprocess.run(['sh','-ec',helper+'\nguest_root_mountpoint "'+str(up)+'"'],env=env,check=True)
   self.assertFalse((up/'xbin').exists())
   (stage/'data/oneos_root/enabled').touch()
   subprocess.run(['sh','-ec',helper+'\nguest_root_mountpoint "'+str(up)+'"'],env=env,check=True)
   self.assertTrue((up/'xbin').is_dir());self.assertFalse((stage/'rootfs/system/xbin').exists())
 def test_bind_remount_has_explicit_source_and_target(self):
  script=(ROOT/'switcher/assets/guest_runtime.sh').read_text()
  snippet=script.split('    if [ -f /data/adb/ksu/.allowlist ]',1)[1].split('\n    fi',1)[0]
  # Run only the real remount/cleanup branch, substituting a fixture target.
  snippet=snippet[snippet.index('        if ! "$busy" mount -o remount,bind,ro'):]
  with tempfile.TemporaryDirectory() as d:
   base=Path(d);(base/'allowlist.saved').write_text('preserved grants')
   busy=base/'busybox';busy.write_text('#!/bin/sh\n[ "$#" = 5 ] && [ "$1" = mount ] && [ "$2" = -o ] && [ "$3" = remount,bind,ro ]\n');busy.chmod(0o755)
   subprocess.run(['sh','-ec',snippet.replace('/data/adb/ksu/.allowlist',str(base/'target'))],env={**os.environ,'B':d,'busy':str(busy)},check=True)
   self.assertTrue((base/'allowlist.protected').exists())
class PrivateBindTest(unittest.TestCase):
 def check_bind(self,kind):
  script=(ROOT/'switcher/assets/guest_runtime.sh').read_text()
  start=script.index('verify_private_adb_bind() {')
  function=script[start:script.index('\n}',start)+2]
  with tempfile.TemporaryDirectory() as d:
   base=Path(d);private=base/'private';(private/'modules').mkdir(parents=True)
   root=base/'rootfs';(root/'data').mkdir(parents=True)
   if kind=='wrong-root':(root/'data/adb').mkdir()
   else:(root/'data/adb').symlink_to(private)
   foreign=base/'foreign';foreign.mkdir()
   busy=base/'busybox'
   busy.write_text('#!'+sys.executable+'\nimport os,sys\nassert sys.argv[1:5]==["stat","-L","-c","%d:%i"]\np=sys.argv[-1]\nif os.getenv("BAD_MODULE_BIND") and p.endswith("/rootfs/data/adb/modules"):p=os.environ["FOREIGN"]\ns=os.stat(p)\nprint(str(s.st_dev)+":"+str(s.st_ino))\n');busy.chmod(0o755)
   env={**os.environ,'B':str(busy),'A':str(private),'R':str(root),'FOREIGN':str(foreign)}
   if kind=='wrong-modules':env['BAD_MODULE_BIND']='1'
   result=subprocess.run(['sh','-ec',function+'\nverify_private_adb_bind'],env=env,capture_output=True,text=True)
   self.assertEqual(kind=='valid',result.returncode==0,result.stderr)
 def test_private_root_and_modules_match(self):self.check_bind('valid')
 def test_host_adb_view_is_rejected(self):self.check_bind('wrong-root')
 def test_nested_modules_overmount_is_rejected(self):self.check_bind('wrong-modules')
 def run_return(self,same,strict=False,policy_ok=True):
  with tempfile.TemporaryDirectory() as d:
   S=Path(d);B=S/'tmp/guest_runtime_baseline';B.mkdir(parents=True);(S/'data/oneos_root').mkdir(parents=True)
   (S/'data/oneos_root/enabled').write_text('')
   if strict:(S/'data/oneos_root/strict_return').write_text('')
   (B/'ready').write_text('');(B/'boot').write_text(Path('/proc/sys/kernel/random/boot_id').read_text())
   (B/'root').write_text('allow 10300 unmount=0\nmanager 10250\n')
   now='manager 10250\nallow 10300 unmount=0\n' if same else 'manager 10250\n'
   (S/'guest_root').write_text('#!/bin/sh\nprintf "'+now.replace('\n','\\n')+'"\n');(S/'guest_root').chmod(0o755)
   pol=S/'policy';pol.write_text('p')
   (B/'selinux').write_text(subprocess.run(['sha256sum',str(pol)],capture_output=True,text=True).stdout)
   if not policy_ok:pol.write_text('q')
   mods=subprocess.run("awk '{print $1, $2, $6}' /proc/modules | sort",shell=True,capture_output=True,text=True).stdout
   (B/'kernel-modules').write_text(mods)
   pl=S/'packages.list';pl.write_text('a 10001\n');pl.chmod(0o640);ino=pl.stat().st_ino
   r=subprocess.run(['sh',str(ROOT/'switcher/assets/guest_runtime.sh'),'verify-return'],env={**os.environ,'STAGE':d,'ONEOS_PKG_LIST':str(pl)},capture_output=True,text=True)
   self.assertEqual(('a 10001\n',0o640),(pl.read_text(),pl.stat().st_mode&0o777));self.assertFalse((S/'packages.list.oneos').exists())
   self.renamed=pl.stat().st_ino!=ino
   return r.returncode,r.stdout
 def test_matching_grants_return_in_place(self):
  rc,out=self.run_return(True);self.assertEqual(0,rc,out);self.assertIn('match baseline',out);self.assertNotIn('changed',out);self.assertFalse(self.renamed)
 def test_changed_grants_are_said_and_still_return_in_place(self):
  rc,out=self.run_return(False);self.assertEqual(0,rc,out)
  self.assertIn('at the switch: allow 10300 unmount=0;manager 10250;',out);self.assertIn('at the return: manager 10250;',out);self.assertIn('returning in place',out);self.assertTrue(self.renamed);self.assertIn('put in place again; root provider now: manager 10250;',out)
 def test_strict_return_and_a_changed_policy_still_reboot(self):
  self.assertEqual(1,self.run_return(False,strict=True)[0]);self.assertEqual(1,self.run_return(False,policy_ok=False)[0])
if __name__=='__main__': unittest.main()
