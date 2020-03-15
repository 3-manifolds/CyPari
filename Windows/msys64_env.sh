# This sets up a reasonable environment for python development on
# msys64 You can add this to the end of your .bash_profile, or source
# it.  It assumes that you have installed the python.org 32-bit Python
# 2.7 in C:\Python27 and their 64-bit Python 2.7 in C:\Python27_64.
# It also assumes that you have installed "Visual C++ for Python" from
# Microsoft.
# https://www.microsoft.com/en-us/download/details.aspx?id=44266

if [ $(uname) = "MINGW64_NT-6.1" ] ; then
    export PATH="/c/Python27_64:/c/Python27_64/Scripts:/c/emacs-24.5/bin:/c/Program Files (x86)/Common Files/Microsoft/Visual C++ for Python/9.0/VC/bin:/c/Program Files (x86)/Common Files/Microsoft/Visual C++ for Python/9.0/WinSDK/Bin:$PATH"
else
    export PATH="/c/Python27:/c/Python27/Scripts:/c/emacs-24.5/bin:/c/Program Files (x86)/Common Files/Microsoft/Visual C++ for Python/9.0/VC/bin:/c/Program Files (x86)/Common Files/Microsoft/Visual C++ for Python/9.0/WinSDK/Bin:$PATH"
fi

# Run bash inside a winpty wrapper to make it possible to run python
# interactively from a mintty terminal.  Install winpty with:
# pacman -S winpty
winpty bash; exit

