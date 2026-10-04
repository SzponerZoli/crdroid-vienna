# usage: cpio_add.py in.cpio out.cpio spec...   spec: D:path:mode  |  F:path:localfile:mode
# Adds or replaces entries in a newc cpio archive (uid/gid 0, existing entries keep their place).
import sys


def pad(n):
    return (-n) % 4


def build(src, dst, specs):
    d = open(src, 'rb').read()
    ents = []
    i = 0
    while True:
        f = [int(d[i + 6 + 8 * k:i + 14 + 8 * k], 16) for k in range(13)]
        ns, fs = f[11], f[6]
        name = d[i + 110:i + 110 + ns - 1].decode()
        j = i + 110 + ns
        j += pad(j)
        data = d[j:j + fs]
        k = j + fs
        k += pad(k)
        ents.append([f, name, data])
        i = k
        if name == 'TRAILER!!!':
            break
    for spec in specs:
        p = spec.split(':')
        if p[0] == 'D':
            path, mode, data = p[1], 0o040000 | int(p[2], 8), b''
        else:
            path, mode, data = p[1], 0o100000 | int(p[3], 8), open(p[2], 'rb').read()
        for e in ents:
            if e[1] == path:
                e[0][1] = mode
                e[2] = data
                break
        else:
            ents.insert(len(ents) - 1, [[0x7ffe0000 + len(ents), mode, 0, 0, 1 if p[0] == 'F' else 2,
                                         0, 0, 0, 0, 0, 0, 0, 0], path, data])
    out = bytearray()
    for f, name, data in ents:
        f[11] = len(name) + 1
        f[6] = len(data)
        h = b'070701' + ''.join('%08X' % v for v in f).encode() + name.encode() + b'\0'
        out += h + b'\0' * pad(len(h)) + data + b'\0' * pad(len(data))
    out += b'\0' * ((-len(out)) % 512)
    open(dst, 'wb').write(out)


if __name__ == '__main__':
    build(sys.argv[1], sys.argv[2], sys.argv[3:])
