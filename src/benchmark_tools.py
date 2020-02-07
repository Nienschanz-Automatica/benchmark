import os
import cv2
import yaml
from datetime import datetime
from openvino.inference_engine import IENetwork, IEPlugin

from src.Threads import InferExecutorThread
from src.InferExecutor import InferExecutor
from src.Stats import  *

with open("benchmark.cfg", "r") as stream:
    benchmark_config = yaml.safe_load(stream)

devices = benchmark_config["devices"]
devices = devices.strip(" ,")
devices = devices.split(",")
devices = [device.strip(" ") for device in devices]

save_logs_every_minutes = benchmark_config["save_logs_every_minutes"]
path_to_cpu_extention = benchmark_config["path_to_cpu_extention"]
request_num = benchmark_config["request_num"]
now = datetime.now().strftime("%d-%m-%Y|%H:%M:%S")
current_logs_dir = os.path.join("logs", now)


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
            listeners.append(CpuStatsListener(current_logs_dir, save_logs_every_minutes))
        elif device == "HDDL":
            path_to_daemon = "/opt/intel/openvino/deployment_tools/inference_engine/external/hddl/bin/"
            listeners.append(HddlStatsListener(path_to_daemon, current_logs_dir, save_logs_every_minutes))
    listeners.append(RamListener(current_logs_dir, save_logs_every_minutes))
    return listeners