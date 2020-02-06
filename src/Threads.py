from threading import Thread
from src.Stats import HDDLStatsListener
from time import sleep
from datetime import datetime

class InferExecutorThread(Thread):
    def __init__(self, device, infer_executor):
        Thread.__init__(self)
        self.name = device
        self.executor = infer_executor

    def run(self):
        while True:
            self.executor.update()


class ListenersThreads(Thread):
    def __init__(self, listeners_list):
        Thread.__init__(self)
        self.listeners = listeners_list
        self.hddl_listener = None
        print(len(self.listeners))
        for idx, listener in enumerate(self.listeners):
            if isinstance(listener, HDDLStatsListener):
                print("HDDL")
                self.hddl_listener = self.listeners.pop(idx)
        print(len(self.listeners))
        sleep(5)

    def run(self):
        while True:
            self.update_listeners()

    def update_listeners(self):
        now = datetime.now()
        now = now.strftime("%H:%M:%S")
        if self.hddl_listener is not None:
            print("test1")
            sleep(5)
            ret = self.hddl_listener.update(now)
            print(ret)
            if ret:
                self.hddl_listener.info()
                for listener in self.listeners:
                    listener.info()
                    listener.update(now)
        else:
            print("test2")
            for listener in self.listeners:
                listener.info()
                listener.update(now)
            sleep(5)