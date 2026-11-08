import struct, pathlib

rom = pathlib.Path("/home/phlip9/dev/dotfiles/notes/gpu.rom").read_bytes()
off = 0
idx = 0
while off + 0x1c <= len(rom):
    if rom[off:off+2] != b"\x55\xaa":
        break
    pcir_off = struct.unpack_from("<H", rom, off + 0x18)[0]
    if pcir_off == 0 or off + pcir_off + 0x18 > len(rom):
        break

    # PCIR data structure is at pcir_off; parse minimally needed fields.
    hdr = rom[off + pcir_off:off + pcir_off + 0x18]
    if hdr[:4] != b"PCIR":
        break

    vend, dev = struct.unpack_from("<HH", hdr, 4)
    imagelen = struct.unpack_from("<H", hdr, 0x10)[0]
    imagetype = hdr[0x14]
    indi = hdr[0x15]

    size = imagelen * 512
    print(
        f"Image {idx}: vend=0x{vend:04x} dev=0x{dev:04x} "
        f"type={imagetype} size={size} start=0x{off:x} last={bool(indi & 0x80)}"
    )
    block = rom[off:off+size]
    if imagetype == 3:  # EFI image
        out = "/home/phlip9/dev/dotfiles/notes/gpu-rom-image%d.bin" % idx
        pathlib.Path(out).write_bytes(block)
        mz = block.find(b"MZ")
        if mz != -1:
            efi = "/home/phlip9/dev/dotfiles/notes/gpu-rom-image%d.efi" % idx
            pathlib.Path(efi).write_bytes(block[mz:])
            print(f"  wrote {out} and EFI payload {efi}")
        else:
            print(f"  wrote {out} (no MZ found inside)")
    off += size
    idx += 1
