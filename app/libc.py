import ctypes

dll = ctypes.CDLL("libc.so.6")

CLONE_NEWPID = 0x20000000


def unshare(flags: int):
    return dll.unshare(flags)
