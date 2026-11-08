package com.android.server.locksettings;

import android.service.gatekeeper.GateKeeperResponse;
import android.service.gatekeeper.IGateKeeperService;
import android.util.Slog;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.security.MessageDigest;
import java.security.SecureRandom;

import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;

/**
 * OneOS: the guest's own gatekeeper, in software, inside the guest's
 * system_server. The phone's gatekeeper HAL holds One UI's lock; the guest
 * never reaches it (guest_no_gatekeeper.py). This one lets ColorOS set and
 * check its own PIN, pattern or password. State: /data/system/oneos_gk (the
 * guest's staged /data).
 */
public final class OneOSGateKeeper extends IGateKeeperService.Stub {
    private static final String TAG = "OneOSGateKeeper";
    private static final File DIR = new File("/data/system/oneos_gk");
    private static final byte[] MAGIC = {'O', 'G', 'K', '1'};
    // magic(4) uid(4) sid(8) salt(16) mac(32)
    private static final int HANDLE_LEN = 64;
    private static OneOSGateKeeper sInstance;

    private final SecureRandom mRandom = new SecureRandom();
    private byte[] mKey;

    public static synchronized OneOSGateKeeper get() {
        if (sInstance == null) sInstance = new OneOSGateKeeper();
        return sInstance;
    }

    private synchronized byte[] key() {
        if (mKey != null) return mKey;
        File f = new File(DIR, "key");
        byte[] k = read(f, 32);
        if (k == null) {
            k = new byte[32];
            mRandom.nextBytes(k);
            write(f, k);
        }
        mKey = k;
        return k;
    }

    private byte[] mac(byte[]... parts) {
        try {
            Mac m = Mac.getInstance("HmacSHA256");
            m.init(new SecretKeySpec(key(), "HmacSHA256"));
            for (byte[] p : parts) if (p != null) m.update(p);
            return m.doFinal();
        } catch (Exception e) {
            throw new IllegalStateException(e);
        }
    }

    private static byte[] read(File f, int len) {
        if (!f.isFile() || f.length() != len) return null;
        byte[] b = new byte[len];
        try (FileInputStream in = new FileInputStream(f)) {
            int n = 0;
            while (n < len) {
                int r = in.read(b, n, len - n);
                if (r < 0) return null;
                n += r;
            }
            return b;
        } catch (Exception e) {
            Slog.w(TAG, "read " + f + ": " + e);
            return null;
        }
    }

    private static void write(File f, byte[] b) {
        try {
            DIR.mkdirs();
            File tmp = new File(f.getPath() + ".tmp");
            try (FileOutputStream out = new FileOutputStream(tmp)) {
                out.write(b);
                out.getFD().sync();
            }
            if (!tmp.renameTo(f)) throw new IllegalStateException("rename");
        } catch (Exception e) {
            Slog.e(TAG, "write " + f + ": " + e);
        }
    }

    private static File sidFile(int uid) {
        return new File(DIR, "sid_" + uid);
    }

    private synchronized long sid(int uid) {
        byte[] b = read(sidFile(uid), 8);
        return b == null ? 0 : ByteBuffer.wrap(b).getLong();
    }

    private synchronized void setSid(int uid, long sid) {
        if (sid == 0) {
            sidFile(uid).delete();
        } else {
            write(sidFile(uid), ByteBuffer.allocate(8).putLong(sid).array());
        }
    }

    private byte[] handle(int uid, long sid, byte[] password) {
        byte[] salt = new byte[16];
        mRandom.nextBytes(salt);
        ByteBuffer b = ByteBuffer.allocate(HANDLE_LEN);
        b.put(MAGIC).putInt(uid).putLong(sid).put(salt);
        byte[] head = new byte[32];
        System.arraycopy(b.array(), 0, head, 0, 32);
        b.put(mac(head, password));
        return b.array();
    }

    /** The handle's SID when it is this uid's and [password] matches, else 0. */
    private long check(int uid, byte[] handle, byte[] password) {
        if (handle == null || handle.length != HANDLE_LEN || password == null) return 0;
        ByteBuffer b = ByteBuffer.wrap(handle);
        for (byte m : MAGIC) if (b.get() != m) return 0;
        if (b.getInt() != uid) return 0;
        long sid = b.getLong();
        byte[] head = new byte[32];
        System.arraycopy(handle, 0, head, 0, 32);
        byte[] want = mac(head, password);
        byte[] got = new byte[32];
        System.arraycopy(handle, 32, got, 0, 32);
        return MessageDigest.isEqual(want, got) && sid != 0 ? sid : 0;
    }

    @Override
    public synchronized GateKeeperResponse enroll(int uid, byte[] currentHandle, byte[] currentPassword, byte[] desiredPassword) {
        if (desiredPassword == null) return GateKeeperResponse.createGenericResponse(GateKeeperResponse.RESPONSE_ERROR);
        long sid = 0;
        if (currentHandle != null) {
            sid = check(uid, currentHandle, currentPassword);
            if (sid == 0) return GateKeeperResponse.createGenericResponse(GateKeeperResponse.RESPONSE_ERROR);
        }
        if (sid == 0) {
            do sid = mRandom.nextLong(); while (sid == 0);
        }
        setSid(uid, sid);
        return GateKeeperResponse.createOkResponse(handle(uid, sid, desiredPassword), false);
    }

    @Override
    public GateKeeperResponse verify(int uid, byte[] handle, byte[] password) {
        return verifyChallenge(uid, 0, handle, password);
    }

    @Override
    public GateKeeperResponse verifyChallenge(int uid, long challenge, byte[] handle, byte[] password) {
        long sid = check(uid, handle, password);
        if (sid == 0) return GateKeeperResponse.createGenericResponse(GateKeeperResponse.RESPONSE_ERROR);
        // hw_auth_token_t: version, challenge, user_id, authenticator_id,
        // authenticator_type (BE), timestamp (BE), hmac. Not signed with the
        // phone's key: the phone's keystore takes no token from the guest.
        ByteBuffer t = ByteBuffer.allocate(69).order(ByteOrder.LITTLE_ENDIAN);
        t.put((byte) 0).putLong(challenge).putLong(sid).putLong(0);
        t.order(ByteOrder.BIG_ENDIAN).putInt(1).putLong(android.os.SystemClock.elapsedRealtime());
        return GateKeeperResponse.createOkResponse(t.array(), false);
    }

    @Override
    public long getSecureUserId(int uid) {
        return sid(uid);
    }

    @Override
    public void clearSecureUserId(int uid) {
        setSid(uid, 0);
    }

    @Override
    public void reportDeviceSetupComplete() {
    }
}
