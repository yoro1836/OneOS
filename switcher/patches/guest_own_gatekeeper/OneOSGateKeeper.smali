.class public final Lcom/android/server/locksettings/OneOSGateKeeper;
.super Landroid/service/gatekeeper/IGateKeeperService$Stub;
.source "OneOSGateKeeper.java"


# static fields
.field private static final DIR:Ljava/io/File;

.field private static final HANDLE_LEN:I = 0x40

.field private static final MAGIC:[B

.field private static final TAG:Ljava/lang/String; = "OneOSGateKeeper"

.field private static sInstance:Lcom/android/server/locksettings/OneOSGateKeeper;


# instance fields
.field private mKey:[B

.field private final mRandom:Ljava/security/SecureRandom;


# direct methods
.method static constructor <clinit>()V
    .registers 2

    .line 27
    new-instance v0, Ljava/io/File;

    const-string v1, "/data/system/oneos_gk"

    invoke-direct {v0, v1}, Ljava/io/File;-><init>(Ljava/lang/String;)V

    sput-object v0, Lcom/android/server/locksettings/OneOSGateKeeper;->DIR:Ljava/io/File;

    .line 28
    const/4 v0, 0x4

    new-array v0, v0, [B

    fill-array-data v0, :array_12

    sput-object v0, Lcom/android/server/locksettings/OneOSGateKeeper;->MAGIC:[B

    return-void

    :array_12
    .array-data 1
        0x4ft
        0x47t
        0x4bt
        0x31t
    .end array-data
.end method

.method public constructor <init>()V
    .registers 2

    .line 25
    invoke-direct {p0}, Landroid/service/gatekeeper/IGateKeeperService$Stub;-><init>()V

    .line 33
    new-instance v0, Ljava/security/SecureRandom;

    invoke-direct {v0}, Ljava/security/SecureRandom;-><init>()V

    iput-object v0, p0, Lcom/android/server/locksettings/OneOSGateKeeper;->mRandom:Ljava/security/SecureRandom;

    return-void
.end method

.method private check(I[B[B)J
    .registers 13

    .line 126
    const-wide/16 v0, 0x0

    if-eqz p2, :cond_4e

    array-length v2, p2

    const/16 v3, 0x40

    if-ne v2, v3, :cond_4e

    if-nez p3, :cond_c

    goto :goto_4e

    .line 127
    :cond_c
    invoke-static {p2}, Ljava/nio/ByteBuffer;->wrap([B)Ljava/nio/ByteBuffer;

    move-result-object v2

    .line 128
    sget-object v3, Lcom/android/server/locksettings/OneOSGateKeeper;->MAGIC:[B

    array-length v4, v3

    const/4 v5, 0x0

    move v6, v5

    :goto_15
    if-ge v6, v4, :cond_23

    aget-byte v7, v3, v6

    invoke-virtual {v2}, Ljava/nio/ByteBuffer;->get()B

    move-result v8

    if-eq v8, v7, :cond_20

    return-wide v0

    :cond_20
    add-int/lit8 v6, v6, 0x1

    goto :goto_15

    .line 129
    :cond_23
    invoke-virtual {v2}, Ljava/nio/ByteBuffer;->getInt()I

    move-result v3

    if-eq v3, p1, :cond_2a

    return-wide v0

    .line 130
    :cond_2a
    invoke-virtual {v2}, Ljava/nio/ByteBuffer;->getLong()J

    move-result-wide v2

    .line 131
    const/16 p1, 0x20

    new-array v4, p1, [B

    .line 132
    invoke-static {p2, v5, v4, v5, p1}, Ljava/lang/System;->arraycopy(Ljava/lang/Object;ILjava/lang/Object;II)V

    .line 133
    filled-new-array {v4, p3}, [[B

    move-result-object p3

    invoke-direct {p0, p3}, Lcom/android/server/locksettings/OneOSGateKeeper;->mac([[B)[B

    move-result-object p3

    .line 134
    new-array v4, p1, [B

    .line 135
    invoke-static {p2, p1, v4, v5, p1}, Ljava/lang/System;->arraycopy(Ljava/lang/Object;ILjava/lang/Object;II)V

    .line 136
    invoke-static {p3, v4}, Ljava/security/MessageDigest;->isEqual([B[B)Z

    move-result p1

    if-eqz p1, :cond_4d

    cmp-long p1, v2, v0

    if-eqz p1, :cond_4d

    move-wide v0, v2

    :cond_4d
    return-wide v0

    .line 126
    :cond_4e
    :goto_4e
    return-wide v0
.end method

.method public static declared-synchronized get()Lcom/android/server/locksettings/OneOSGateKeeper;
    .registers 2

    const-class v0, Lcom/android/server/locksettings/OneOSGateKeeper;

    monitor-enter v0

    .line 37
    :try_start_3
    sget-object v1, Lcom/android/server/locksettings/OneOSGateKeeper;->sInstance:Lcom/android/server/locksettings/OneOSGateKeeper;

    if-nez v1, :cond_e

    new-instance v1, Lcom/android/server/locksettings/OneOSGateKeeper;

    invoke-direct {v1}, Lcom/android/server/locksettings/OneOSGateKeeper;-><init>()V

    sput-object v1, Lcom/android/server/locksettings/OneOSGateKeeper;->sInstance:Lcom/android/server/locksettings/OneOSGateKeeper;

    .line 38
    :cond_e
    sget-object v1, Lcom/android/server/locksettings/OneOSGateKeeper;->sInstance:Lcom/android/server/locksettings/OneOSGateKeeper;
    :try_end_10
    .catchall {:try_start_3 .. :try_end_10} :catchall_12

    monitor-exit v0

    return-object v1

    .line 36
    :catchall_12
    move-exception v1

    :try_start_13
    monitor-exit v0
    :try_end_14
    .catchall {:try_start_13 .. :try_end_14} :catchall_12

    throw v1
.end method

.method private handle(IJ[B)[B
    .registers 8

    .line 114
    const/16 v0, 0x10

    new-array v0, v0, [B

    .line 115
    iget-object v1, p0, Lcom/android/server/locksettings/OneOSGateKeeper;->mRandom:Ljava/security/SecureRandom;

    invoke-virtual {v1, v0}, Ljava/security/SecureRandom;->nextBytes([B)V

    .line 116
    const/16 v1, 0x40

    invoke-static {v1}, Ljava/nio/ByteBuffer;->allocate(I)Ljava/nio/ByteBuffer;

    move-result-object v1

    .line 117
    sget-object v2, Lcom/android/server/locksettings/OneOSGateKeeper;->MAGIC:[B

    invoke-virtual {v1, v2}, Ljava/nio/ByteBuffer;->put([B)Ljava/nio/ByteBuffer;

    move-result-object v2

    invoke-virtual {v2, p1}, Ljava/nio/ByteBuffer;->putInt(I)Ljava/nio/ByteBuffer;

    move-result-object p1

    invoke-virtual {p1, p2, p3}, Ljava/nio/ByteBuffer;->putLong(J)Ljava/nio/ByteBuffer;

    move-result-object p1

    invoke-virtual {p1, v0}, Ljava/nio/ByteBuffer;->put([B)Ljava/nio/ByteBuffer;

    .line 118
    const/16 p1, 0x20

    new-array p2, p1, [B

    .line 119
    invoke-virtual {v1}, Ljava/nio/ByteBuffer;->array()[B

    move-result-object p3

    const/4 v0, 0x0

    invoke-static {p3, v0, p2, v0, p1}, Ljava/lang/System;->arraycopy(Ljava/lang/Object;ILjava/lang/Object;II)V

    .line 120
    filled-new-array {p2, p4}, [[B

    move-result-object p1

    invoke-direct {p0, p1}, Lcom/android/server/locksettings/OneOSGateKeeper;->mac([[B)[B

    move-result-object p1

    invoke-virtual {v1, p1}, Ljava/nio/ByteBuffer;->put([B)Ljava/nio/ByteBuffer;

    .line 121
    invoke-virtual {v1}, Ljava/nio/ByteBuffer;->array()[B

    move-result-object p1

    return-object p1
.end method

.method private declared-synchronized key()[B
    .registers 4

    monitor-enter p0

    .line 42
    :try_start_1
    iget-object v0, p0, Lcom/android/server/locksettings/OneOSGateKeeper;->mKey:[B

    if-eqz v0, :cond_9

    iget-object v0, p0, Lcom/android/server/locksettings/OneOSGateKeeper;->mKey:[B
    :try_end_7
    .catchall {:try_start_1 .. :try_end_7} :catchall_28

    monitor-exit p0

    return-object v0

    .line 43
    :cond_9
    :try_start_9
    new-instance v0, Ljava/io/File;

    sget-object v1, Lcom/android/server/locksettings/OneOSGateKeeper;->DIR:Ljava/io/File;

    const-string v2, "key"

    invoke-direct {v0, v1, v2}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V

    .line 44
    const/16 v1, 0x20

    invoke-static {v0, v1}, Lcom/android/server/locksettings/OneOSGateKeeper;->read(Ljava/io/File;I)[B

    move-result-object v2

    .line 45
    if-nez v2, :cond_24

    .line 46
    new-array v2, v1, [B

    .line 47
    iget-object v1, p0, Lcom/android/server/locksettings/OneOSGateKeeper;->mRandom:Ljava/security/SecureRandom;

    invoke-virtual {v1, v2}, Ljava/security/SecureRandom;->nextBytes([B)V

    .line 48
    invoke-static {v0, v2}, Lcom/android/server/locksettings/OneOSGateKeeper;->write(Ljava/io/File;[B)V

    .line 50
    :cond_24
    iput-object v2, p0, Lcom/android/server/locksettings/OneOSGateKeeper;->mKey:[B
    :try_end_26
    .catchall {:try_start_9 .. :try_end_26} :catchall_28

    .line 51
    monitor-exit p0

    return-object v2

    .line 41
    :catchall_28
    move-exception v0

    :try_start_29
    monitor-exit p0
    :try_end_2a
    .catchall {:try_start_29 .. :try_end_2a} :catchall_28

    throw v0
.end method

.method private varargs mac([[B)[B
    .registers 6

    .line 56
    const-string v0, "HmacSHA256"

    :try_start_2
    invoke-static {v0}, Ljavax/crypto/Mac;->getInstance(Ljava/lang/String;)Ljavax/crypto/Mac;

    move-result-object v1

    .line 57
    new-instance v2, Ljavax/crypto/spec/SecretKeySpec;

    invoke-direct {p0}, Lcom/android/server/locksettings/OneOSGateKeeper;->key()[B

    move-result-object v3

    invoke-direct {v2, v3, v0}, Ljavax/crypto/spec/SecretKeySpec;-><init>([BLjava/lang/String;)V

    invoke-virtual {v1, v2}, Ljavax/crypto/Mac;->init(Ljava/security/Key;)V

    .line 58
    array-length v0, p1

    const/4 v2, 0x0

    :goto_14
    if-ge v2, v0, :cond_20

    aget-object v3, p1, v2

    if-eqz v3, :cond_1d

    invoke-virtual {v1, v3}, Ljavax/crypto/Mac;->update([B)V

    :cond_1d
    add-int/lit8 v2, v2, 0x1

    goto :goto_14

    .line 59
    :cond_20
    invoke-virtual {v1}, Ljavax/crypto/Mac;->doFinal()[B

    move-result-object p1
    :try_end_24
    .catch Ljava/lang/Exception; {:try_start_2 .. :try_end_24} :catch_25

    return-object p1

    .line 60
    :catch_25
    move-exception p1

    .line 61
    new-instance v0, Ljava/lang/IllegalStateException;

    invoke-direct {v0, p1}, Ljava/lang/IllegalStateException;-><init>(Ljava/lang/Throwable;)V

    throw v0
.end method

.method private static read(Ljava/io/File;I)[B
    .registers 8

    .line 66
    invoke-virtual {p0}, Ljava/io/File;->isFile()Z

    move-result v0

    const/4 v1, 0x0

    if-eqz v0, :cond_64

    invoke-virtual {p0}, Ljava/io/File;->length()J

    move-result-wide v2

    int-to-long v4, p1

    cmp-long v0, v2, v4

    if-eqz v0, :cond_11

    goto :goto_64

    .line 67
    :cond_11
    new-array v0, p1, [B

    .line 68
    :try_start_13
    new-instance v2, Ljava/io/FileInputStream;

    invoke-direct {v2, p0}, Ljava/io/FileInputStream;-><init>(Ljava/io/File;)V
    :try_end_18
    .catch Ljava/lang/Exception; {:try_start_13 .. :try_end_18} :catch_38

    .line 69
    const/4 v3, 0x0

    .line 70
    :goto_19
    if-ge v3, p1, :cond_33

    .line 71
    sub-int v4, p1, v3

    :try_start_1d
    invoke-virtual {v2, v0, v3, v4}, Ljava/io/FileInputStream;->read([BII)I

    move-result v4
    :try_end_21
    .catchall {:try_start_1d .. :try_end_21} :catchall_29

    .line 72
    if-gez v4, :cond_27

    .line 76
    :try_start_23
    invoke-virtual {v2}, Ljava/io/FileInputStream;->close()V
    :try_end_26
    .catch Ljava/lang/Exception; {:try_start_23 .. :try_end_26} :catch_38

    .line 72
    return-object v1

    .line 73
    :cond_27
    add-int/2addr v3, v4

    .line 74
    goto :goto_19

    .line 68
    :catchall_29
    move-exception p1

    :try_start_2a
    invoke-virtual {v2}, Ljava/io/FileInputStream;->close()V
    :try_end_2d
    .catchall {:try_start_2a .. :try_end_2d} :catchall_2e

    goto :goto_32

    :catchall_2e
    move-exception v0

    :try_start_2f
    invoke-virtual {p1, v0}, Ljava/lang/Throwable;->addSuppressed(Ljava/lang/Throwable;)V

    :goto_32
    throw p1

    .line 75
    :cond_33
    nop

    .line 76
    invoke-virtual {v2}, Ljava/io/FileInputStream;->close()V
    :try_end_37
    .catch Ljava/lang/Exception; {:try_start_2f .. :try_end_37} :catch_38

    .line 75
    return-object v0

    .line 76
    :catch_38
    move-exception p1

    .line 77
    invoke-static {p0}, Ljava/lang/String;->valueOf(Ljava/lang/Object;)Ljava/lang/String;

    move-result-object p0

    invoke-static {p1}, Ljava/lang/String;->valueOf(Ljava/lang/Object;)Ljava/lang/String;

    move-result-object p1

    new-instance v0, Ljava/lang/StringBuilder;

    invoke-direct {v0}, Ljava/lang/StringBuilder;-><init>()V

    const-string v2, "read "

    invoke-virtual {v0, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0, p0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p0

    const-string v0, ": "

    invoke-virtual {p0, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p0

    invoke-virtual {p0, p1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p0

    invoke-virtual {p0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p0

    const-string p1, "OneOSGateKeeper"

    invoke-static {p1, p0}, Landroid/util/Slog;->w(Ljava/lang/String;Ljava/lang/String;)I

    .line 78
    return-object v1

    .line 66
    :cond_64
    :goto_64
    return-object v1
.end method

.method private declared-synchronized setSid(IJ)V
    .registers 6

    monitor-enter p0

    .line 106
    const-wide/16 v0, 0x0

    cmp-long v0, p2, v0

    if-nez v0, :cond_f

    .line 107
    :try_start_7
    invoke-static {p1}, Lcom/android/server/locksettings/OneOSGateKeeper;->sidFile(I)Ljava/io/File;

    move-result-object p1

    invoke-virtual {p1}, Ljava/io/File;->delete()Z

    goto :goto_24

    .line 109
    :cond_f
    invoke-static {p1}, Lcom/android/server/locksettings/OneOSGateKeeper;->sidFile(I)Ljava/io/File;

    move-result-object p1

    const/16 v0, 0x8

    invoke-static {v0}, Ljava/nio/ByteBuffer;->allocate(I)Ljava/nio/ByteBuffer;

    move-result-object v0

    invoke-virtual {v0, p2, p3}, Ljava/nio/ByteBuffer;->putLong(J)Ljava/nio/ByteBuffer;

    move-result-object p2

    invoke-virtual {p2}, Ljava/nio/ByteBuffer;->array()[B

    move-result-object p2

    invoke-static {p1, p2}, Lcom/android/server/locksettings/OneOSGateKeeper;->write(Ljava/io/File;[B)V
    :try_end_24
    .catchall {:try_start_7 .. :try_end_24} :catchall_26

    .line 111
    :goto_24
    monitor-exit p0

    return-void

    .line 105
    :catchall_26
    move-exception p1

    :try_start_27
    monitor-exit p0
    :try_end_28
    .catchall {:try_start_27 .. :try_end_28} :catchall_26

    throw p1
.end method

.method private declared-synchronized sid(I)J
    .registers 4

    monitor-enter p0

    .line 101
    :try_start_1
    invoke-static {p1}, Lcom/android/server/locksettings/OneOSGateKeeper;->sidFile(I)Ljava/io/File;

    move-result-object p1

    const/16 v0, 0x8

    invoke-static {p1, v0}, Lcom/android/server/locksettings/OneOSGateKeeper;->read(Ljava/io/File;I)[B

    move-result-object p1

    .line 102
    if-nez p1, :cond_10

    const-wide/16 v0, 0x0

    goto :goto_18

    :cond_10
    invoke-static {p1}, Ljava/nio/ByteBuffer;->wrap([B)Ljava/nio/ByteBuffer;

    move-result-object p1

    invoke-virtual {p1}, Ljava/nio/ByteBuffer;->getLong()J

    move-result-wide v0
    :try_end_18
    .catchall {:try_start_1 .. :try_end_18} :catchall_1a

    :goto_18
    monitor-exit p0

    return-wide v0

    .line 100
    :catchall_1a
    move-exception p1

    :try_start_1b
    monitor-exit p0
    :try_end_1c
    .catchall {:try_start_1b .. :try_end_1c} :catchall_1a

    throw p1
.end method

.method private static sidFile(I)Ljava/io/File;
    .registers 5

    .line 97
    new-instance v0, Ljava/io/File;

    sget-object v1, Lcom/android/server/locksettings/OneOSGateKeeper;->DIR:Ljava/io/File;

    new-instance v2, Ljava/lang/StringBuilder;

    invoke-direct {v2}, Ljava/lang/StringBuilder;-><init>()V

    const-string v3, "sid_"

    invoke-virtual {v2, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v2

    invoke-virtual {v2, p0}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    move-result-object p0

    invoke-virtual {p0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p0

    invoke-direct {v0, v1, p0}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V

    return-object v0
.end method

.method private static write(Ljava/io/File;[B)V
    .registers 5

    .line 84
    :try_start_0
    sget-object v0, Lcom/android/server/locksettings/OneOSGateKeeper;->DIR:Ljava/io/File;

    invoke-virtual {v0}, Ljava/io/File;->mkdirs()Z

    .line 85
    new-instance v0, Ljava/io/File;

    invoke-virtual {p0}, Ljava/io/File;->getPath()Ljava/lang/String;

    move-result-object v1

    new-instance v2, Ljava/lang/StringBuilder;

    invoke-direct {v2}, Ljava/lang/StringBuilder;-><init>()V

    invoke-virtual {v2, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    const-string v2, ".tmp"

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v1

    invoke-direct {v0, v1}, Ljava/io/File;-><init>(Ljava/lang/String;)V

    .line 86
    new-instance v1, Ljava/io/FileOutputStream;

    invoke-direct {v1, v0}, Ljava/io/FileOutputStream;-><init>(Ljava/io/File;)V
    :try_end_26
    .catch Ljava/lang/Exception; {:try_start_0 .. :try_end_26} :catch_4c

    .line 87
    :try_start_26
    invoke-virtual {v1, p1}, Ljava/io/FileOutputStream;->write([B)V

    .line 88
    invoke-virtual {v1}, Ljava/io/FileOutputStream;->getFD()Ljava/io/FileDescriptor;

    move-result-object p1

    invoke-virtual {p1}, Ljava/io/FileDescriptor;->sync()V
    :try_end_30
    .catchall {:try_start_26 .. :try_end_30} :catchall_42

    .line 89
    :try_start_30
    invoke-virtual {v1}, Ljava/io/FileOutputStream;->close()V

    .line 90
    invoke-virtual {v0, p0}, Ljava/io/File;->renameTo(Ljava/io/File;)Z

    move-result p1

    if-eqz p1, :cond_3a

    .line 93
    goto :goto_77

    .line 90
    :cond_3a
    new-instance p1, Ljava/lang/IllegalStateException;

    const-string v0, "rename"

    invoke-direct {p1, v0}, Ljava/lang/IllegalStateException;-><init>(Ljava/lang/String;)V

    throw p1
    :try_end_42
    .catch Ljava/lang/Exception; {:try_start_30 .. :try_end_42} :catch_4c

    .line 86
    :catchall_42
    move-exception p1

    :try_start_43
    invoke-virtual {v1}, Ljava/io/FileOutputStream;->close()V
    :try_end_46
    .catchall {:try_start_43 .. :try_end_46} :catchall_47

    goto :goto_4b

    :catchall_47
    move-exception v0

    :try_start_48
    invoke-virtual {p1, v0}, Ljava/lang/Throwable;->addSuppressed(Ljava/lang/Throwable;)V

    :goto_4b
    throw p1
    :try_end_4c
    .catch Ljava/lang/Exception; {:try_start_48 .. :try_end_4c} :catch_4c

    .line 91
    :catch_4c
    move-exception p1

    .line 92
    invoke-static {p0}, Ljava/lang/String;->valueOf(Ljava/lang/Object;)Ljava/lang/String;

    move-result-object p0

    invoke-static {p1}, Ljava/lang/String;->valueOf(Ljava/lang/Object;)Ljava/lang/String;

    move-result-object p1

    new-instance v0, Ljava/lang/StringBuilder;

    invoke-direct {v0}, Ljava/lang/StringBuilder;-><init>()V

    const-string v1, "write "

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0, p0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p0

    const-string v0, ": "

    invoke-virtual {p0, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p0

    invoke-virtual {p0, p1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p0

    invoke-virtual {p0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p0

    const-string p1, "OneOSGateKeeper"

    invoke-static {p1, p0}, Landroid/util/Slog;->e(Ljava/lang/String;Ljava/lang/String;)I

    .line 94
    :goto_77
    return-void
.end method


# virtual methods
.method public clearSecureUserId(I)V
    .registers 4

    .line 179
    const-wide/16 v0, 0x0

    invoke-direct {p0, p1, v0, v1}, Lcom/android/server/locksettings/OneOSGateKeeper;->setSid(IJ)V

    .line 180
    return-void
.end method

.method public declared-synchronized enroll(I[B[B[B)Landroid/service/gatekeeper/GateKeeperResponse;
    .registers 9

    monitor-enter p0

    .line 141
    const/4 v0, -0x1

    if-nez p4, :cond_c

    :try_start_4
    invoke-static {v0}, Landroid/service/gatekeeper/GateKeeperResponse;->createGenericResponse(I)Landroid/service/gatekeeper/GateKeeperResponse;

    move-result-object p1
    :try_end_8
    .catchall {:try_start_4 .. :try_end_8} :catchall_a

    monitor-exit p0

    return-object p1

    .line 140
    :catchall_a
    move-exception p1

    goto :goto_3c

    .line 142
    :cond_c
    nop

    .line 143
    const-wide/16 v1, 0x0

    if-eqz p2, :cond_1f

    .line 144
    :try_start_11
    invoke-direct {p0, p1, p2, p3}, Lcom/android/server/locksettings/OneOSGateKeeper;->check(I[B[B)J

    move-result-wide p2

    .line 145
    cmp-long v3, p2, v1

    if-nez v3, :cond_20

    invoke-static {v0}, Landroid/service/gatekeeper/GateKeeperResponse;->createGenericResponse(I)Landroid/service/gatekeeper/GateKeeperResponse;

    move-result-object p1
    :try_end_1d
    .catchall {:try_start_11 .. :try_end_1d} :catchall_a

    monitor-exit p0

    return-object p1

    .line 143
    :cond_1f
    move-wide p2, v1

    .line 147
    :cond_20
    cmp-long v0, p2, v1

    if-nez v0, :cond_2e

    .line 148
    :cond_24
    :try_start_24
    iget-object p2, p0, Lcom/android/server/locksettings/OneOSGateKeeper;->mRandom:Ljava/security/SecureRandom;

    invoke-virtual {p2}, Ljava/security/SecureRandom;->nextLong()J

    move-result-wide p2

    cmp-long v0, p2, v1

    if-eqz v0, :cond_24

    .line 150
    :cond_2e
    invoke-direct {p0, p1, p2, p3}, Lcom/android/server/locksettings/OneOSGateKeeper;->setSid(IJ)V

    .line 151
    invoke-direct {p0, p1, p2, p3, p4}, Lcom/android/server/locksettings/OneOSGateKeeper;->handle(IJ[B)[B

    move-result-object p1

    const/4 p2, 0x0

    invoke-static {p1, p2}, Landroid/service/gatekeeper/GateKeeperResponse;->createOkResponse([BZ)Landroid/service/gatekeeper/GateKeeperResponse;

    move-result-object p1
    :try_end_3a
    .catchall {:try_start_24 .. :try_end_3a} :catchall_a

    monitor-exit p0

    return-object p1

    .line 140
    :goto_3c
    :try_start_3c
    monitor-exit p0
    :try_end_3d
    .catchall {:try_start_3c .. :try_end_3d} :catchall_a

    throw p1
.end method

.method public getSecureUserId(I)J
    .registers 4

    .line 174
    invoke-direct {p0, p1}, Lcom/android/server/locksettings/OneOSGateKeeper;->sid(I)J

    move-result-wide v0

    return-wide v0
.end method

.method public reportDeviceSetupComplete()V
    .registers 1

    .line 184
    return-void
.end method

.method public verify(I[B[B)Landroid/service/gatekeeper/GateKeeperResponse;
    .registers 10

    .line 156
    const-wide/16 v2, 0x0

    move-object v0, p0

    move v1, p1

    move-object v4, p2

    move-object v5, p3

    invoke-virtual/range {v0 .. v5}, Lcom/android/server/locksettings/OneOSGateKeeper;->verifyChallenge(IJ[B[B)Landroid/service/gatekeeper/GateKeeperResponse;

    move-result-object p1

    return-object p1
.end method

.method public verifyChallenge(IJ[B[B)Landroid/service/gatekeeper/GateKeeperResponse;
    .registers 10

    .line 161
    invoke-direct {p0, p1, p4, p5}, Lcom/android/server/locksettings/OneOSGateKeeper;->check(I[B[B)J

    move-result-wide p4

    .line 162
    const-wide/16 v0, 0x0

    cmp-long p1, p4, v0

    if-nez p1, :cond_10

    const/4 p1, -0x1

    invoke-static {p1}, Landroid/service/gatekeeper/GateKeeperResponse;->createGenericResponse(I)Landroid/service/gatekeeper/GateKeeperResponse;

    move-result-object p1

    return-object p1

    .line 166
    :cond_10
    const/16 p1, 0x45

    invoke-static {p1}, Ljava/nio/ByteBuffer;->allocate(I)Ljava/nio/ByteBuffer;

    move-result-object p1

    sget-object v2, Ljava/nio/ByteOrder;->LITTLE_ENDIAN:Ljava/nio/ByteOrder;

    invoke-virtual {p1, v2}, Ljava/nio/ByteBuffer;->order(Ljava/nio/ByteOrder;)Ljava/nio/ByteBuffer;

    move-result-object p1

    .line 167
    const/4 v2, 0x0

    invoke-virtual {p1, v2}, Ljava/nio/ByteBuffer;->put(B)Ljava/nio/ByteBuffer;

    move-result-object v3

    invoke-virtual {v3, p2, p3}, Ljava/nio/ByteBuffer;->putLong(J)Ljava/nio/ByteBuffer;

    move-result-object p2

    invoke-virtual {p2, p4, p5}, Ljava/nio/ByteBuffer;->putLong(J)Ljava/nio/ByteBuffer;

    move-result-object p2

    invoke-virtual {p2, v0, v1}, Ljava/nio/ByteBuffer;->putLong(J)Ljava/nio/ByteBuffer;

    .line 168
    sget-object p2, Ljava/nio/ByteOrder;->BIG_ENDIAN:Ljava/nio/ByteOrder;

    invoke-virtual {p1, p2}, Ljava/nio/ByteBuffer;->order(Ljava/nio/ByteOrder;)Ljava/nio/ByteBuffer;

    move-result-object p2

    const/4 p3, 0x1

    invoke-virtual {p2, p3}, Ljava/nio/ByteBuffer;->putInt(I)Ljava/nio/ByteBuffer;

    move-result-object p2

    invoke-static {}, Landroid/os/SystemClock;->elapsedRealtime()J

    move-result-wide p3

    invoke-virtual {p2, p3, p4}, Ljava/nio/ByteBuffer;->putLong(J)Ljava/nio/ByteBuffer;

    .line 169
    invoke-virtual {p1}, Ljava/nio/ByteBuffer;->array()[B

    move-result-object p1

    invoke-static {p1, v2}, Landroid/service/gatekeeper/GateKeeperResponse;->createOkResponse([BZ)Landroid/service/gatekeeper/GateKeeperResponse;

    move-result-object p1

    return-object p1
.end method
