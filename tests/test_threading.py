import random
import time
from threading import Thread


class InferExecutorThread(Thread):
    def __init__(self, device, infer_executor):
        Thread.__init__(self)
        self.name = device
        self.executor = infer_executor

    def run(self):
        while True:
            self.executor.update()


# def create_threads():
#     """
#     Создаем группу потоков
#     """
#     for i in range(5):
#         name = "Thread #%s" % (i + 1)
#         my_thread = MyThread(name)
#         my_thread.start()
#
#
# if __name__ == "__main__":
#     create_threads()