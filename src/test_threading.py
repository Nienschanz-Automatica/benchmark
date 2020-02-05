import random
import time
from threading import Thread


class InferExecutorThread(Thread):
    def __init__(self, device, infer_executor, input_data):
        Thread.__init__(self)
        self.name = device
        self.executor = infer_executor
        self.input_data = input_data

    def run(self):
        while True:
            self.executor.update(self.input_data)


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