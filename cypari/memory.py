from sys import platform
import subprocess
from subprocess import Popen, PIPE

wmic = 'C:\Windows\System32\wbem\wmic'

def total_ram():
    if platform.startswith('linux'):
        out, err = Popen(['free', '-b'],
                         stdin=PIPE, stdout=PIPE, stderr=PIPE).communicate()
        out = out.decode()
        lines = out.split('\n')
        for line in lines:
            words = line.split()
            if words[0] == 'Mem:':
                return int(words[1])
    elif platform == 'darwin':
        out, err = Popen(['sysctl', 'hw.memsize'],
                         stdin=PIPE, stdout=PIPE, stderr=PIPE).communicate()
        return int(out.split()[1])
    elif platform == 'win32':
        startup = subprocess.STARTUPINFO()
        startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        proc = Popen([wmic, 'computersystem', 'get', 'TotalPhysicalMemory'],
                     stdin=PIPE, stdout=PIPE, stderr=PIPE,
                     startupinfo=startup)
        out, err = proc.communicate()
        return int(out.split()[1])

            
            
