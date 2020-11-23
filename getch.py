# taken from https://code.activestate.com/recipes/134892/
# originally written by Danny Yoo
#
# fun note: it was posted 18 years ago and still works!

import signal,threading,time,os
import ctypes
import threading
import time

def async_raise(thread_obj, exception):
    print('aaaaa')

    """ Raises an exception inside an arbitrary active :class:`~threading.Thread`.
    Parameters
    ----------
    thread_obj : :class:`~threading.Thread`
        The target thread.
    exception : ``Exception``
        The exception class to be raised.
    Raises
    ------
    ValueError
        The specified :class:`~threading.Thread` is not active.
    SystemError
        The raise operation failed, the interpreter has been left in an inconsistent state.
    """
    target_tid = thread_obj.ident
    if target_tid not in {thread.ident for thread in threading.enumerate()}:
        raise ValueError('Invalid thread object, cannot find thread identity among currently active threads.')

    affected_count = ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(target_tid), ctypes.py_object(exception))

    if affected_count == 0:
        raise ValueError('Invalid thread identity, no thread has been affected.')
    elif affected_count > 1:
        ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(target_tid), ctypes.c_long(0))
        raise SystemError("PyThreadState_SetAsyncExc failed, broke the interpreter state.")


class ThreadExc(threading.Thread):
    def get_id(self):

        # returns id of the respective thread
        if hasattr(self, '_thread_id'):
            return self._thread_id
        for id, thread in threading._active.items():
            if thread is self:
                return id

    def raise_exception(self):
        thread_id = self.get_id()
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id,
              ctypes.py_object(SystemExit))
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
            print('Exception raise failure')

class _Getch:
    def __init__(self):
        try:
            self.impl = _GetchWindows()
        except ImportError:
            self.impl = _GetchUnix()

    def __call__(self,timeout=0):
        # if timeout:
        #    self.set_timeout(timeout)

        return self.impl()

    # def set_timeout(self,t):
        # def alarm(t):
        #     time.sleep(t)
        #     getch_thread.raise_exception()
        # threading.Thread(target=alarm,args=[t]).start()



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
# def getch(timeout=0):
#     global getch_thread

#     getch_thread = ThreadExc(target=getch_start,args=[timeout])
#     getch_thread.start()


# TODO
# getch(1)
# while True:
#     print('yes')
#     time.sleep(0.2)
