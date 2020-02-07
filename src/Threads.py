from threading import Thread, Event
from src.Stats import HDDLStatsListener
from time import sleep
from datetime import datetime

class InferExecutorThread(Thread):
    def __init__(self, device, infer_executor):
        Thread.__init__(self)
        self.name = device
        self.executor = infer_executor
        self._stopper = Event()

    def del_executor(self):
        del self.executor

    def run(self):
        while True:
            if self.stopped():
                return
            self.executor.update()

    def stop(self):
        self.executor.stop()
        self._stopper.set()

    def stopped(self):
        return self._stopper.is_set()

class ListenersThread(Thread):
    def __init__(self, listeners_list):
        Thread.__init__(self)
        self.listeners = listeners_list
        self.hddl_listener = None
        self._stopper = Event()
        for idx, listener in enumerate(self.listeners):
            if isinstance(listener, HDDLStatsListener):
                self.hddl_listener = self.listeners.pop(idx)

    def run(self):
        while True:
            if self.stopped():
                return
            self.update_listeners()

    def stop(self):
        self._stopper.set()

    def stopped(self):
        return self._stopper.is_set()

    def update_listeners(self):
        now = datetime.now()
        now = now.strftime("%H:%M:%S")
        if self.hddl_listener is not None:
            ret, now = self.hddl_listener.update()
            if ret:
                self.hddl_listener.info()
                for listener in self.listeners:
                    listener.update(now)
                    listener.info()
                print("\n")
        else:
            for listener in self.listeners:
                listener.update(now)
                listener.info()
            print("\n")
            sleep(5)