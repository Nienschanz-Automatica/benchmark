import os
import getpass
from time import time
import cv2
from openvino.inference_engine import IENetwork, IEPlugin, IECore
from src.Queue import Queue
from src.RequestId import RequestId
# from src.Visualizer import SegmentationVisualizer, DetectionVisualizer


class IENetMeta(object):
    def __init__(self, path_to_model_xml, path_to_model_bin, requests_num):
        self.ie_network = IENetwork(path_to_model_xml, path_to_model_bin)

        self.input_blob = next(iter(self.ie_network.inputs))
        self.output_blob = next(iter(self.ie_network.outputs))

        self.requests_num = requests_num
        self.exec_net = self.init_exec_net()
        self.init_input_blob_params()

        self.requests_queue = Queue(requests_num)
        self.current_request_id = RequestId(requests_num)
        self.start_current_infer_times_queue = Queue(requests_num)

        self.outputs_buffer = None

    # def init_visualizer(self, path_to_visualizer_cfg, net_type, confidence_thresh=0.5):
    #     if net_type.lower() == "segmentation":
    #         self.visualizer = SegmentationVisualizer(path_to_visualizer_cfg, confidence_thresh)
    #     else:
    #         self.visualizer = DetectionVisualizer(path_to_visualizer_cfg, confidence_thresh)

    def init_outputs_buffer(self, buffer_size):
        self.outputs_buffer = Queue(buffer_size)

    def get_current_request_id(self):
        return self.current_request_id.id

    def init_exec_net(self):
        pass

    def start_single_infer(self, frame):
        input_blob = self.frame_to_blob(frame)
        self.make_request(self.current_request_id.id, input_blob)
        self.requests_queue.push(self.current_request_id.id)
        self.start_current_infer_times_queue.push(time())

    def update_current_request_id(self):
        self.current_request_id += 1

    def init_input_blob_params(self, swapRB=True):
        input_info = self.ie_network.inputs
        if 'data' in input_info.keys():
            _, _, self.input_h, self.input_w = input_info['data'].shape
        else:
            self.input_h, self.input_w = 512, 512
        self.swapRB = swapRB

    def make_request(self, request_id, input_blob):
        self.exec_net.start_async(request_id=request_id,
                                  inputs={self.input_blob: input_blob})

    def request_is_done(self, request_id):
        return self.exec_net.requests[request_id].wait(1) == 0

    def get_request_result(self, request_id):
        return self.exec_net.requests[request_id].outputs[self.output_blob]

    def frame_to_blob(self, frame):
        dst_shape = (self.input_w, self.input_h)
        blob = cv2.dnn.blobFromImages([frame], 1, dst_shape, swapRB=self.swapRB)
        return blob

    def visualize(self, frame, net_output):
        frame = self.visualizer.visualize(frame, net_output)
        return frame

class IENetCPU(IENetMeta):
    def __init__(self, path_to_model_xml, path_to_model_bin, requests_num):
        IENetMeta.__init__(self, path_to_model_xml, path_to_model_bin, requests_num)

    def init_exec_net(self):
        plugin = IEPlugin(device="CPU")
        user_name = getpass.getuser()
        cpu_extention_dir = "/home/{}/inference_engine_samples_build/intel64/Release/lib/".format(user_name)
        cpu_extention_filename = "libcpu_extension.so"
        path_to_cpu_extention = os.path.join(cpu_extention_dir, cpu_extention_filename)
        plugin.add_cpu_extension(path_to_cpu_extention)
        config = {"PERF_COUNT": "NO",  # Сбор статистики
                  "EXCLUSIVE_ASYNC_REQUESTS": "NO",  # Последовательное выполнение запросов (для нескольких НС)
                  "CPU_THREADS_NUM": "0",  # Количество ядер процессора (0 - все ядра)
                  "CPU_THROUGHPUT_STREAMS": "CPU_THROUGHPUT_AUTO"}

        exec_net = plugin.load(network=self.ie_network,
                               config=config,
                               num_requests=self.requests_num)
        return exec_net


class IENetHDDL(IENetMeta):
    def __init__(self, path_to_model_xml, path_to_model_bin, requests_num):
        IENetMeta.__init__(self, path_to_model_xml, path_to_model_bin, requests_num)

    def init_exec_net(self):
        plugin = IEPlugin(device="HDDL")
        config = {}
        exec_net = plugin.load(network=self.ie_network,
                               config=config,
                               num_requests=self.requests_num)
        return exec_net


class IENetObjectBuilder():
    def __init__(self, path_to_model_xml, path_to_model_bin, requests_num, device):
        self.path_to_model_xml = path_to_model_xml
        self.path_to_model_bin = path_to_model_bin
        self.requests_num = requests_num
        self.device = device

    def build_net_object(self):
        if self.device == "CPU":
            return IENetCPU(self.path_to_model_xml, self.path_to_model_bin, self.requests_num)
        else:
            return IENetHDDL(self.path_to_model_xml, self.path_to_model_bin, self.requests_num)