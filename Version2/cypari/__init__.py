import os
old_cwd = os.getcwd()
install_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
os.chdir(install_path)
__all__ = ['pari']
from cypari.gen import gen as pari_gen
from cypari.pari_instance import pari
from cypari.handle_error import PariError
os.chdir(old_cwd)

