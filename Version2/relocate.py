import os, sys, sysconfig
from subprocess import Popen, PIPE, call
from glob import glob
from os import path

def fix_libpari_path(lib, target):
    print 'fixing %s.'%lib
    current_path = None
    out, err = Popen(['otool', '-L', lib], stdout=PIPE).communicate()
    lines = out.split('\n')
    for line in lines:
        if line.find('libpari') > 0:
            current_path = line.split()[0]
            break
    if current_path:
        call(['install_name_tool', '-change', current_path, target, lib])
    else:
        print 'Error: no reference to libpari in %s'%lib

def make_relocatable():
    lib_dir_format = '{dirname}.{platform}-{major}.{minor}'
    lib_dir = lib_dir_format.format(dirname='lib',
                                    platform=sysconfig.get_platform(),
                                    major=sys.version_info.major,
                                    minor=sys.version_info.minor)
    lib_path = os.path.join('build', lib_dir, 'cypari')
    shared_lib_glob = os.path.join(lib_path, '*.so')
    pari_lib_glob = os.path.join(lib_path, 'libpari*')
    shared_libs = glob(shared_lib_glob)
    pari_lib = glob(pari_lib_glob)[0]
    pari_lib_name = path.basename(pari_lib)
    target = path.join('@loader_path', pari_lib_name)
    for shared_lib in shared_libs:
        fix_libpari_path(shared_lib, target)
    print 'Resetting the ID of the Pari library.'
    call(['install_name_tool', '-id', pari_lib_name, pari_lib])

