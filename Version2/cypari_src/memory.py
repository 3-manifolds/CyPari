from sys import platform
from subprocess import Popen, PIPE

wmic = 'C:\Windows\System32\wbem\wmic'

def total_ram():
    if platform.startswith('linux'):
        out, err = Popen(['free', '-b'], stdout=PIPE).communicate()
        out = out.decode()
        lines = out.split('\n')
        for line in lines:
            words = line.split()
            if words[0] == 'Mem:':
                return int(words[1])
    elif platform == 'darwin':
        out, err = Popen(['sysctl', 'hw.memsize'], stdout=PIPE).communicate()
        return int(out.split()[1])
    elif platform == 'win32':
         proc = Popen([wmic, 'computersystem', 'get', 'TotalPhysicalMemory'],
                      stdout=PIPE)
         out, err = proc.communicate()
         return int(out.split()[1])

            
            
