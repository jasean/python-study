
def apply_async(func, args, *, callback):
    f = func(*args)
    callback(f)

def add(*args):
    return sum(args)

from queue import Queue
from functools import wraps
import pdb

class Async:
    def __init__(self, func, args):
        self.func = func
        self.args = args

def inline_async(func):
    @wraps(func)
    def wrapper(*args):
        f = func(*args)
        result_queue = Queue()
        result_queue.put(None)
        while True:
            result = result_queue.get()
            try:
                a = f.send(result)
                apply_async(a.func, a.args, callback=result_queue.put)
            except StopIteration:
                break
    return wrapper

@inline_async
def test():
    pdb.set_trace()
    r = yield Async(add, (2,3))
    print(r)
    r = yield Async(add, (5,6))
    print(r)


def consumer():
    print('start...')
    pdb.set_trace()
    r = ''
    while True:
        n = yield r
        if not n:
            return
        print('[CONSUMER] Consuming %s...' % n)
        r = '200 OK'

def produce(c):
    pdb.set_trace()
    r = c.send(None)
    n = 0
    while n < 5:
        n = n + 1
        print('[PRODUCER] Producing %s...' % n)
        r = c.send(n)
        print('[PRODUCER] Consumer return: %s' % r)
    c.close()

if __name__ == '__main__':
    # test()
    c = consumer()
    produce(c)
