import shutil

import pexpect


def start(cmd):
    """Starts cmd in a proper terminal

    * Propagates terminal size correctly
    """
    (columns, lines) = shutil.get_terminal_size()
    pexpect.spawn(cmd[0], cmd[1:], dimensions=(lines, columns)).interact()
