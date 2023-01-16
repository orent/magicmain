import sys
import os
import errno

MFD_CLOEXEC = 1


def _make_memfd_create():
    import ctypes
    libc = ctypes.CDLL(None)

    try:
        _memfd = libc.memfd_create
    except AttributeError:
        if sys.platform.startswith('linux'):
            libc.syscall.argtypes = ctypes.c_int, ctypes.c_char_p, ctypes.c_int
            SYS_memfd = 319 if sys.maxsize > 2**32 else 356
            _memfd = lambda name, flags: libc.syscall(SYS_memfd, name, flags)
        else:
            _memfd = lambda name, flags: ctypes.set_errno(errno.ENOSYS) or -1

    try:
        from os import fsencode 
    except ImportError:
        fsencode = unicode.encode

    def memfd_create(name, flags=MFD_CLOEXEC):
        if not isinstance(name, bytes):
            name = fsencode(name)
        res = _memfd(name, flags)
        if res == -1:
            errno = ctypes.get_errno()
            raise OSError(errno, os.strerror(errno))
        return res

    return memfd_create

try:
    from os import memfd_create
except ImportError:
    memfd_create = _make_memfd_create()

if __name__ == '__main__':
    print('Creating memfd handle. fd={}'.format(memfd_create('')))
