from sys import platform
from subprocess import Popen, PIPE

def total_ram():
    if platform == 'linux2':
        out, err = Popen(['free', '-b'], stdout=PIPE).communicate()
        lines = out.split('\n')
        for line in lines:
            words = line.split()
            if words[0] == 'Mem:':
                return int(words[1])
    elif platform == 'darwin':
        out, err = Popen(['sysctl', 'hw.memsize'], stdout=PIPE).communicate()
        return int(out.split()[1])

            
            
