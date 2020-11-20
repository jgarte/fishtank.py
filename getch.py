# taken from https://code.activestate.com/recipes/134892/
# originally written by Danny Yoo, timeout added by me
#
# fun note: it was posted 18 years ago and still works!

import signal

class _Getch:
    def __init__(self):
        try:
            self.impl = _GetchWindows()
        except ImportError:
            self.impl = _GetchUnix()

    def __call__(self,timeout=0):
        # stop execution at timeout
        #signal.alarm(timeout)
        return self.impl()

class _GetchUnix:
    def __init__(self):
        import tty, sys

    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


class _GetchWindows:
    def __init__(self):
        import msvcrt

    def __call__(self):
        global key

        import msvcrt
        return msvcrt.getch()

# nicer namespace
getch = _Getch()
