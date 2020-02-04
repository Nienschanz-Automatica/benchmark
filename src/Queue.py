class Queue:
    def __init__(self, max_size):
        self.max_size = max_size
        self.queue = []

    def __len__(self):
        return len(self.queue)

    def push(self, item):
        self.queue.insert(0, item)
        self.cut_queue()

    def get(self):
        return self.queue.pop(-1)

    def cut_queue(self):
        if len(self.queue) > self.max_size:
            self.queue = self.queue[:-1]