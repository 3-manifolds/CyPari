import sys, os, requests, subprocess

if sys.version_info.major == 2:
    sys.exit()
    
sf_url = 'https://sourceforge.net/projects/mingw-w64/files/Toolchains%20targetting%20Win32/Personal%20Builds/mingw-builds/8.1.0/threads-posix/dwarf/i686-8.1.0-release-posix-dwarf-rt_v6-rev0.7z/download'

toolchain_path = os.path.join('libcache', 'mingw32',
                              'i686-8.1.0-release-posix-dwarf-rt_v6-rev0')
if os.path.isdir(toolchain_path):
    sys.exit()
if not os.path.isdir('libcache'):
    os.mkdir('libcache')
print('Downloading toolchain ...')
response = requests.get(sf_url, allow_redirects=True, timeout=30)
print('Received %d bytes.'%len(response.content))
with open('toolchain.7z', 'wb') as output:
    output.write(response.content)
print('Unzipping toolchain ...')
junk = subprocess.check_output(['7z', 'x', 'toolchain.7z'])
os.remove('toolchain.7z')
os.rename('mingw32', os.path.join('libcache', 'mingw32'))
print('Done')
