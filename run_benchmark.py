# from statistics import median
import os
import cv2
import getpass
from openvino.inference_engine import IENetwork, IEPlugin

user_name = getpass.getuser()
cpu_extention_dir = "/home/{}/inference_engine_samples_build/intel64/Release/lib/".format(user_name)
cpu_extention_filename = "libcpu_extension.so"
path_to_cpu_extention = os.path.join(cpu_extention_dir, cpu_extention_filename)

device = "CPU"
request_num = 32

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

xml_file = "model/road-segmentation-adas-0001.xml"
bin_file = "model/road-segmentation-adas-0001.bin"

ie_network = IENetwork(xml_file, bin_file)

input_info = ie_network.inputs
exe_network = plugin.load(ie_network, request_num)

image = cv2.imread("images/road.jpeg")
_, _, input_h, input_w = input_info["data"].shape
dst_shape = (input_w, input_h)
input_images = cv2.dnn.blobFromImages([image], 1, dst_shape, swapRB=True)
input_images_dict = {"data": input_images}

infer_requests = exe_network.requests
current_inference = 0
previous_inference = 1 - request_num

infer_requests[0].async_infer(input_images_dict)
infer_requests[0].wait()

while True:
    exe_network.start_async(current_inference, input_images_dict)
    if previous_inference >= 0:
        status = infer_requests[previous_inference].wait()

    current_inference += 1
    if current_inference >= request_num:
        current_inference = 0
        # required_inference_requests_were_executed = True

    previous_inference += 1
    if previous_inference >= request_num:
        previous_inference = 0
    # step += 1

# for not_completed_index in range(request_num):
#     if infer_requests[not_completed_index].wait(0) != 0:
#         infer_requests[not_completed_index].wait()