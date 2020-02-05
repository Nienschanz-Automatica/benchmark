import os
import cv2
import getpass
from openvino.inference_engine import IENetwork, IEPlugin
from src.Threads import InferExecutorThread, HddldaemonThread
from src.HddlDaemonListener import HddlDaemonListener

user_name = getpass.getuser()
cpu_extention_dir = "/home/{}/inference_engine_samples_build/intel64/Release/lib/".format(user_name)
cpu_extention_filename = "libcpu_extension.so"
path_to_cpu_extention = os.path.join(cpu_extention_dir, cpu_extention_filename)

devices = ["HDDL", "CPU"]
request_num = 8

xml_file = "model/road-segmentation-adas-0001.xml"
bin_file = "model/road-segmentation-adas-0001.bin"



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
        infer_executor = InferExecutor(exe_network, input_images_dict)
        executor_thread = InferExecutorThread(device, infer_executor)
        threads_list.append(executor_thread)
    return threads_list

daemon_listener = HddlDaemonListener()
while not daemon_listener.is_running():
    pass

daemon_thread = HddldaemonThread(daemon_listener)
daemon_thread.start()

threads_list = build_nets(xml_file, bin_file, devices, 32)
for executor in threads_list:
    executor.start()



# for not_completed_index in range(request_num):
#     if infer_requests[not_completed_index].wait(0) != 0:
#         infer_requests[not_completed_index].wait()