from subprocess import Popen, PIPE, call
from glob import glob
from os import path

shared_libs = glob('*.so')
pari_lib = glob('libpari*')[0]
here = path.abspath('.')
target = path.join(here, pari_lib)

def fix_libpari_path(lib):
   print 'fixing', lib
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
       print 'Error: no reference to libpari in %s'%shared_lib

for shared_lib in shared_libs:
   fix_libpari_path(shared_lib)


