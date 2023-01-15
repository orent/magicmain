# Extend zipimport to load binary extension directly from archive

import sys
import os
import zipimport

try:
    from importlib.machinery import EXTENSION_SUFFIXES, ModuleSpec
    from _imp import create_dynamic
except ImportError:
    # Python 2
    import imp
    EXTENSION_SUFFIXES = [
        x for x, _, type in imp.get_suffixes() if type== imp.C_EXTENSION
    ]

    def ModuleSpec(name, loader, origin=None):
        return name, origin

    def create_dynamic(spec):
        return imp.load_dynamic(*spec)


# Create a temporary file. Return file object and its temporary pathname
# Name hint should appear in /proc/PID/maps
def tmpfile(namehint='', body=None):
    namehint = os.path.basename(namehint)
    try:
        # Linux specific - 100% in memory
        fd = os.memfd_create(namehint)
        f = os.fdopen(fd, 'w+b')
        filename = '/proc/self/fd/{}'.format(fd)
    except (AttributeError, OSError):
        # Portable fallback using temporary file
        import tempfile
        f = tempfile.NamedTemporaryFile(mode='w+b', suffix='-' + namehint)
        filename = f.name
    if body:
        f.write(body)
    return f, filename


class zextimporter(zipimport.zipimporter):
    def find_ext(self, fullname):
        name = fullname.rpartition('.')[2]
        for suffix in EXTENSION_SUFFIXES:
            inarchive = os.path.join(self.prefix, name + suffix)
            if inarchive in self._files:
                return inarchive

    def find_module(self, fullname):
        relpath = self.find_ext(fullname)
        if not relpath:
            return super(zextimporter, self).find_module(fullname)
        return self

    def find_loader(self, fullname):
        relpath = self.find_ext(fullname)
        if not relpath:
            return super(zextimporter, self).find_loader(fullname)
        return self, []

    def load_module(self, fullname):
        relpath = self.find_ext(fullname)
        if not relpath:
            return super(zextimporter, self).load_module(fullname)

        f, tmpf = tmpfile(relpath, self.get_data(relpath))
        spec = ModuleSpec(fullname, self, origin=tmpf)
        with f:
            mod = create_dynamic(spec)
            mod.__file__ = self.get_filename(fullname)
        return mod

    def get_filename(self, fullname):
        return os.path.join(self.archive, self.find_ext(fullname) or '')


def install():
    try:
        sys.path_hooks[sys.path_hooks.index(zipimport.zipimporter)] = zextimporter
    except ValueError:
        pass

    for k, v in list(sys.path_importer_cache.items()):
        if isinstance(v, zipimport.zipimporter) and not isinstance(v, zextimporter):
            del sys.path_importer_cache[k]

install()
