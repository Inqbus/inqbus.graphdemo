import time

""" This is a proper debounce function, the way a electrical engineer
    would think about it.
    This wrapper never calls sleep.  It has two counters: one for successful
    calls, and one for rejected calls.
    If the wrapped function throws an exception, the counters and debounce
    timer are still correct """


class Debounce(object):

    def __init__(self, period):
        # never call the wrapped function more often than this (in seconds)
        self.period = period
        # how many times have we successfully # called the function
        self.count = 0
        # how many times have we rejected the call
        self.count_rejected = 0
        # the last time it was called
        self.last = None

    # force a reset of the timer, aka the next call will always work
    def reset(self):
        self.last = None

    def __call__(self, f):
        def wrapped(inst, attr, old, new):
            now = time.time()
            if self.last is not None:
                # amount of time since last call
                delta = now - self.last
                if delta >= self.period:
                    willcall = True
                else:
                    willcall = False
            else:
                willcall = True  # function has never been called before

            if willcall:
                # set these first incase we throw an exception
                self.last = now  # don't use time.time()
                self.count += 1
                f(inst, attr, old, new)  # call wrapped function
            else:
                self.count_rejected += 1
        return wrapped
