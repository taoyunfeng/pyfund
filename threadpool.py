# -*- coding: UTF-8 -*-

import threading
import queue

all = [
    'threadpool',
    'threadparam'
]

class threadparam(object):
    def __init__(self, poolsize):
        super().__init__()
        self.counter = 0
        self.poolsize = poolsize
        self.inited_ev = threading.Event()
        self.exit_flag = False
        self.task_queue = queue.Queue(0)

class threadtask(threading.Thread):
    def __init__(self, threadarg):
        super().__init__(daemon=True)
        self.threadarg = threadarg

    def run(self):
        threadarg = self.threadarg
        threadarg.counter = threadarg.counter + 1
        if threadarg.counter == threadarg.poolsize:
            threadarg.inited_ev.set()
        while True:
            task = threadarg.task_queue.get()
            if task:
                task[0](*task[1])
            elif threadarg.exit_flag:
                break
            threadarg.task_queue.task_done()
            

class threadpool(object):
    def __init__(self, poolsize):
        super().__init__()
        self.tharg = threadparam(poolsize)
        self.ths = [ threadtask(self.tharg) for i in range(poolsize) ]
        for th in self.ths:
            th.start()
        self.tharg.inited_ev.wait()

    def __del__(self):
        self.shutdown()

    def __stop_all(self, to_exit):
        self.tharg.task_queue.join()
        self.tharg.exit_flag = to_exit
        if to_exit:
            for i in range(self.tharg.poolsize):
                self.tharg.task_queue.put(None)

            for th in self.ths:
                th.join()

            self.ths.clear()

    def shutdown(self):
        self.__stop_all(True)

    def join_all(self):
        self.__stop_all(False)

    def submit(self, target, arg=()):
        self.tharg.task_queue.put((target, arg))

if __name__ == '__main__':

    pool = threadpool(2)
    lock = threading.Lock()
    def test(a, b):
        import time
        time.sleep(1)
        lock.acquire()
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), a, b)
        lock.release()

    for i in range(1, 5, 1):
        pool.submit(test, (i, i ** 2))

    pool.join_all()

    for i in range(1, 5, 1):
        pool.submit(test, (i, i ** 2))

    pool.join_all()
    pool.shutdown()