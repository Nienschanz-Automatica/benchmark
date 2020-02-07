class InferExecutor():
    def __init__(self, exec_net, input_images_dict):
        self.exec_net = exec_net
        self.infer_requests = self.exec_net.requests
        self.current_inference = 0
        self.input_images_dict = input_images_dict
        for i in range(len(self.infer_requests)):
            self.exec_net.start_async(self.current_inference, input_images_dict)
            self.current_inference += 1
            if self.current_inference >= len(self.infer_requests):
                self.current_inference = 0

    def update(self):
        if self.infer_requests[self.current_inference].wait(0.1) == 0:
            self.exec_net.start_async(self.current_inference, self.input_images_dict)
        self.current_inference += 1
        if self.current_inference >= len(self.infer_requests):
            self.current_inference = 0

    def stop(self):
       for i in range(len(self.infer_requests)):
           while not self.infer_requests[self.current_inference].wait(-1) == 0:
               pass