# from statistics import median
import os
import cv2
import getpass
from openvino.inference_engine import IENetwork, IEPlugin
from src.test_threading import InferExecutorThread

user_name = getpass.getuser()
cpu_extention_dir = "/home/{}/inference_engine_samples_build/intel64/Release/lib/".format(user_name)
cpu_extention_filename = "libcpu_extension.so"
path_to_cpu_extention = os.path.join(cpu_extention_dir, cpu_extention_filename)

devices = ["CPU"]
request_num = 32

xml_file = "model/road-segmentation-adas-0001.xml"
bin_file = "model/road-segmentation-adas-0001.bin"

class InferExecutor():
    def __init__(self, exec_net):
        self.exec_net = exec_net
        self.infer_requests = self.exec_net.requests
        self.current_inference = 0
        self.previous_inference = 1 - len(self.infer_requests)

    def update(self, input_images_dict):
        self.exec_net.start_async(self.current_inference, input_images_dict)
        if self.previous_inference >= 0:
            status = self.infer_requests[self.previous_inference].wait(-1)
        self.current_inference += 1
        if self.current_inference >= len(self.infer_requests):
            self.current_inference = 0

        self.previous_inference += 1
        if self.previous_inference >= len(self.infer_requests):
            self.previous_inference = 0

def build_nets(xml_file, bin_file, devices, requests_num):
    threads_list = []
    image = cv2.imread("images/road.jpeg")
    dst_shape = (896, 512)
    input_images = cv2.dnn.blobFromImages([image], 1, dst_shape, swapRB=True)
    input_images_dict = {"data": input_images}

    for device in devices:
        plugin = IEPlugin(device)
        if device == "CPU":
            config = {"CPU_THREADS_NUM": "0", "CPU_THROUGHPUT_STREAMS": str(request_num)}
            plugin.add_cpu_extension(path_to_cpu_extention)
        elif device == "HDDL":
            config = {"LOG_LEVEL": "LOG_INFO",
                      "VPU_LOG_LEVEL": "LOG_INFO"}
        else:
            config = {}

        plugin.set_config(config)
        ie_network = IENetwork(xml_file, bin_file)
        exe_network = plugin.load(ie_network, requests_num)
        infer_executor = InferExecutor(exe_network)
        executor_thread = InferExecutorThread(device, infer_executor, input_images_dict)
        threads_list.append(executor_thread)
    return threads_list



threads_list = build_nets(xml_file, bin_file, devices, 32)
# while True:
for executor in threads_list:
    executor.start()



# for not_completed_index in range(request_num):
#     if infer_requests[not_completed_index].wait(0) != 0:
#         infer_requests[not_completed_index].wait()