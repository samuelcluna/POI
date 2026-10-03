import time

MB = 1024 * 1024
PAGE = 4096


def allocate_and_hold(mb: int, hold_ms: int) -> int:
    buf = bytearray(mb * MB)
    # sem tocar as páginas o kernel não aloca a memória de fato
    for offset in range(0, len(buf), PAGE):
        buf[offset] = 1
    time.sleep(hold_ms / 1000)
    return len(buf)
