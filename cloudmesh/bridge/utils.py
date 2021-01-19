from cloudmesh.common.console import Console
from cloudmesh.common.util import writefile
import os
import subprocess
import platform


# These functions should be moved to cloudmesh.common.utils
def sudo_readfile(filename, split=True, trim=False):
    result = subprocess.getoutput(f"sudo cat {filename}")

    # Trim trailing whitespace
    # This is useful to prevent empty string entries when splitting by '\n'
    if trim:
        result = result.rstrip()

    if split:
        result = result.split('\n')

    return result


def sudo_writefile(filename, content, append=False):
    os.system('mkdir -p ~/.cloudmesh/tmp')
    tmp = "~/.cloudmesh/tmp/tmp.txt"

    if append:
        content = sudo_readfile(filename, split=False) + content

    writefile(tmp, content)

    result = subprocess.getstatusoutput(f"sudo cp {tmp} {filename}")

    # If exit code is not 0
    if result[0] != 0:
        Console.warning(f"{filename} was not created correctly -> {result[1]}")

    return result[1]
