import os
import cv2
import getpass
from datetime import datetime
from openvino.inference_engine import IENetwork, IEPlugin

from src.Stats import *
from src.Threads import ListenersThreads, InferExecutorThread
from src.InferExecutor import InferExecutor


if "logs" not in os.listdir(os.getcwd()):
    os.mkdir("logs")

devices = ["HDDL", "CPU"]
save_every_minutes = 1

now = datetime.now().strftime("%d-%m-%Y|%H:%M:%S")
current_logs_dir = os.path.join("logs", now)
os.mkdir(current_logs_dir)
for device in devices:
    os.mkdir(os.path.join(current_logs_dir, device))
os.mkdir(os.path.join(current_logs_dir, "RAM"))



if "CPU" in devices:
    user_name = getpass.getuser()
    cpu_extention_dir = "/home/{}/inference_engine_samples_build/intel64/Release/lib/".format(user_name)
    cpu_extention_filename = "libcpu_extension.so"
    path_to_cpu_extention = os.path.join(cpu_extention_dir, cpu_extention_filename)
else:
    path_to_cpu_extention = None

request_num = 32

xml_file = "model/road-segmentation-adas-0001.xml"
bin_file = "model/road-segmentation-adas-0001.bin"


def build_executors(xml_file, bin_file, devices, requests_num):
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


def build_listeners(devices):
    listeners = []
    for device in devices:
        if device == "CPU":
            listeners.append(CpuStatsListener(current_logs_dir, save_every_minutes))
        elif device == "HDDL":
            path_to_daemon = "/opt/intel/openvino/deployment_tools/inference_engine/external/hddl/bin/"
            listeners.append(HDDLStatsListener(path_to_daemon, current_logs_dir, save_every_minutes))
    listeners.append(RamListener(current_logs_dir, save_every_minutes))
    return listeners


listeners_list = build_listeners(devices)
listeners_threads = ListenersThreads(listeners_list)

listeners_threads.start()

executors_threads_list = build_executors(xml_file, bin_file, devices, request_num)
for executor_thread in executors_threads_list:
    executor_thread.start()