# We build with -mmacosx-version-min=10.9 so our wheels should work on 10.9 and up.
# However, some build systems (notably Appveyor) name the wheels as being for 10.15
# while others are apparently smart enough to name the wheels as being for 10.9.
# This script renames all wheels in the dist directory to target 10.9.

import os, re
retarget = re.compile('(cypari-.+-macosx_10_)[0-9]+(_.*\.whl)')

for wheel_file in os.listdir('dist'):
    new_name = retarget.sub('\g<1>9\g<2>', wheel_file)
    os.rename(os.path.join('dist', wheel_file), os.path.join('dist', new_name))
                               
