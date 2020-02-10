from threading import Thread, Event
from src.Stats import HddlStatsListener
from time import time, sleep
from datetime import datetime




class InferExecutorThread(Thread):
    def __init__(self, device, infer_executor, running_time):
        Thread.__init__(self)
        self.name = device
        self.executor = infer_executor
        self._stopper = Event()
        self.running_time = running_time
        self.start_time = time()

    def del_executor(self):
        del self.executor

    def run(self):
        while True:
            if self.running_time > 0:
                if self.running_time < (time() - self.start_time)/60:
                    return
            if self.stopped():
                return
            self.executor.update()

    def stop(self):
        self.executor.stop()
        self._stopper.set()

    def stopped(self):
        return self._stopper.is_set()

class ListenersThread(Thread):
    def __init__(self, listeners_list, running_time):
        Thread.__init__(self)
        self.listeners = listeners_list
        self.hddl_listener = None
        self._stopper = Event()
        self.start_time = time()

        self.running_time = running_time
        for idx, listener in enumerate(self.listeners):
            if isinstance(listener, HddlStatsListener):
                self.hddl_listener = self.listeners.pop(idx)

    def run(self):
        while True:
            if self.running_time > 0:
                if self.running_time < (time() - self.start_time)/60:
                    return
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