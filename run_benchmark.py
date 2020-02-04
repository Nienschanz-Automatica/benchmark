import cv2
import yaml
from os import path as osp
from src.config_tools import parse_devices
from src.IENet import IENetCPU, IENetHDDL
from src.vusualize_utils import prepare_net_output, visualize


path_to_benchmark_config = "benchmark.cfg"
with open(path_to_benchmark_config, "r") as stream:
    config = yaml.safe_load(stream)

net_xml = config["model_xml_name"]
net_bin = config["model_bin_name"]
net_xml_path = osp.join("model", net_xml)
net_bin_path = osp.join("model", net_bin)

nets = []
devices = parse_devices(config["devices"])

for device in devices:
    if device == "CPU":
        requests_num = config["cpu_request_num"]
        net = IENetCPU(net_xml_path, net_bin_path, requests_num)
    elif device == "HDDL":
        requests_num = config["hddl_request_num"]
        net = IENetHDDL(net_xml_path, net_bin_path, requests_num)
    else:
        raise ValueError("device should be CPU or HDDL")
    nets.append(net)

for device in devices:
    if device == "CPU":
        requests_num = config["cpu_request_num"]
        net = IENetCPU(net_xml_path, net_bin_path, requests_num)
    elif device == "HDDL":
        requests_num = config["hddl_request_num"]
        net = IENetHDDL(net_xml_path, net_bin_path, requests_num)
    else:
        raise ValueError("device should be CPU or HDDL")
    net.init_input_blob_params()
    nets.append(net)

img = cv2.imread("images/road.jpeg")

for net in nets:
    for r in range(net.requests_num):
        currnet_req = net.current_request_id
        net.start_single_infer(img)
        net.update_current_request_id()

RUN = True

while RUN:
    for net in nets:
        current_request_id = net.get_current_request_id()
        if net.request_is_done(current_request_id):
            request_result = net.get_request_result(current_request_id)
            img_to_show = img.copy()
            h, w, _ = img_to_show.shape
            img_to_show = cv2.resize(img_to_show, (w//2, h//2))
            img_to_show = visualize(img_to_show, request_result)

            cv2.imshow("result", img_to_show)
            if cv2.waitKey(1) & 0xFF == 27:
                cv2.destroyAllWindows()
                RUN = False
                break

            net.start_single_infer(img)
            net.update_current_request_id()
#
#
