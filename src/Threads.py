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
        for idx, listener in enumerate(self.listeners):
            if isinstance(listener, HDDLStatsListener):
                self.hddl_listener = self.listeners.pop(idx)

    def run(self):
        while True:
            self.update_listeners()

    def update_listeners(self):
        now = datetime.now()
        now = now.strftime("%H:%M:%S")
        if self.hddl_listener is not None:
            ret, now = self.hddl_listener.update()
            if ret:
                self.hddl_listener.info()
                for listener in self.listeners:
                    listener.info()
                    listener.update(now)
        else:
            for listener in self.listeners:
                listener.info()
                listener.update(now)
            sleep(5)