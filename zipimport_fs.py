import sys
import os
import stat
import errno
import io

def zlookup(path):
    for importer in sys.path_importer_cache.values():
        if hasattr(importer, 'archive') and path.startswith(importer.archive + '/'):
            rpath0 = path[len(importer.archive) + 1:]
            for dirsuffix in ('', '/'):
                rpath = rpath0 + dirsuffix
                if rpath in importer._files:
                    return importer, rpath
    raise OSError(errno.ENOENT, 'Path not found within ZIP', path)

def zstat(path):
    importer, rpath = zlookup(path)
    _, _, _, size, ofs, _, _, _ = importer._files[rpath]
    return os.stat_result((
        ( 
            stat.S_IFDIR | 0o555 
            if rpath.endswith('/') else
            stat.S_IFREG | 0o444
        ),              # st_mode
        ofs,            # st_ino
        -id(importer),  # st_dev
        1,              # st_nlink
        0,              # st_uid
        0,              # st_gid
        size,           # st_size
        0,              # st_atime
        0,              # st_mtime
        0,              # st_ctime
    ))

def zopen(filename, mode='rt', *args, **kw):
    importer, rpath = zlookup(filename)
    if rpath.endswith('/'):
        raise OSError(errno.EISDIR, 'Entry within ZIP is a directory', filename)
    data = importer.get_data(rpath)
    if 'b' in mode or bytes is str:
        return io.BytesIO(data)
    else:
        return io.StringIO(data.decode())

def zlistdir(dirpath):
    importer, rpath = zlookup(dirpath)
    if not rpath.endswith('/'):
        raise OSError(errno.ENOTDIR, 'Entry within ZIP is not a directory', dirpath)
    return [
        basename
        for basename, sep, tail in (
            x[len(rpath):].partition('/') 
            for x in importer._files 
            if x.startswith(rpath) 
        )
        if basename and not tail
    ]

try:
    import __builtin__ as builtins
except ImportError:
    import builtins

try:
    builtins._orig_open
except AttributeError:
    builtins._orig_open = builtins.open

def open_wrapper(filename, *args, **kw):
    try:
        return builtins._orig_open(filename, *args, **kw)
    except IOError as e:
        if e.errno != errno.ENOTDIR:
            raise
        return zopen(filename, *args, **kw)

builtins.open = open_wrapper


try:
    os._orig_stat
except AttributeError:
    os._orig_stat = os.stat

def stat_wrapper(pathname):
    try:
        return os._orig_stat(pathname)
    except OSError as e:
        if e.errno != errno.ENOTDIR:
            raise
        return zstat(pathname)

os.stat = stat_wrapper

try:
    os._orig_lstat
except AttributeError:
    os._orig_lstat = os.lstat

def lstat_wrapper(pathname):
    try:
        return os._orig_lstat(pathname)
    except OSError as e:
        if e.errno != errno.ENOTDIR:
            raise
        return zstat(pathname)

os.lstat = lstat_wrapper


try:
    os._orig_listdir
except AttributeError:
    os._orig_listdir = os.listdir

def listdir_wrapper(pathname):
    try:
        return os._orig_listdir(pathname)
    except OSError as e:
        if e.errno != errno.ENOTDIR:
            raise
        return zlistdir(pathname)

os.listdir = listdir_wrapper
