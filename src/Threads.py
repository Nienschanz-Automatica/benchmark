from threading import Thread


class InferExecutorThread(Thread):
    def __init__(self, device, infer_executor):
        Thread.__init__(self)
        self.name = device
        self.executor = infer_executor

    def run(self):
        while True:
            self.executor.update()


class HddldaemonThread(Thread):
    def __init__(self, daemon_listener):
        Thread.__init__(self)
        self.daemon_listener = daemon_listener

    def run(self):
        while True:
            self.daemon_listener.update()