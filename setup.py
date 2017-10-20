import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
#build_exe_options = {"packages": ["os"], "excludes": ["tkinter"]}

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == "win32":
    base = "console"

setup(  name = "Ping dnscrypt",
        version = "0.1",
        description = "Pings through dnscrypt list of servers",
        #options = {"build_exe": build_exe_options},
        executables = [Executable("pingdnscrypt.py", base=base)])