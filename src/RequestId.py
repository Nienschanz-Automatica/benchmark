class RequestId(object):
    def __init__(self, max_val, init_value=0):
        assert isinstance(init_value, int), "init value should be int type"
        self.id = init_value
        self.max_val = max_val

    def __iadd__(self, other):
        self.id += other
        if self.id > self.max_val:
            self.id = self.id - self.max_val
        elif self.id == self.max_val:
            self.id = 0
        return self

    def __repr__(self):
        return "request id: {}".format(self.id)