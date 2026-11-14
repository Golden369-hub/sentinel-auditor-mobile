import zlib
import struct

w, h = 512, 512
raw = bytearray()
for y in range(h):
    raw.append(0)
    for x in range(w):
        if x < 24 or x >= w - 24 or y < 24 or y >= h - 24 or (180 <= x <= 332 and 180 <= y <= 332):
            raw.extend((0, 255, 102))
        else:
            raw.extend((15, 17, 23))

def chunk(tag, data):
    crc = zlib.crc32(tag + data) & 0xffffffff
    return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", crc)

png = (
    b"\x89PNG\r\n\x1a\n"
    + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
    + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    + chunk(b"IEND", b"")
)

with open("icon.png", "wb") as f:
    f.write(png)
