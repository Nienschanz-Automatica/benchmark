import sys
from time import sleep
from subprocess import *
from src.cpu_info_utils import get_system_info


class SystemStatsListener():
    def __init__(self):
        self.command = '/opt/intel/openvino/deployment_tools/inference_engine/external/hddl/bin/hddldaemon'
        self.encoding_type = "utf-8"
        self.counter = 0
        self.daemon = None
        self.running = False
        self.run_daemon()
        self.loading()
        self.info_string = ""

    def loading(self):
        print("Please wait. Loading may take a few minutes.")
        key_words = ["SERVICE", "IS", "READY"]
        animation = "|/-\\"
        counter = 0
        while not self.running:
            data = self.daemon.stdout.readline()
            str_data = data.decode(encoding=self.encoding_type)
            word_in_data = [word in str_data for word in key_words]
            if all(word_in_data):
                self.running = True
            else:
                sys.stdout.write("\r" + "Loading " + animation[counter % len(animation)])
                counter += 1
                sys.stdout.flush()
                sleep(0.5)

    def run_daemon(self):
        self.daemon = Popen(self.command, shell=True, stdout=PIPE)

    def update(self):
        data = self.daemon.stdout.readline()  # Alternatively self.daemon.stdout.read(1024)
        str_data = data.decode(encoding=self.encoding_type)
        if "deviceId" in str_data:
            self.info_string += get_system_info()
            splited = self.split_line(str_data)
            devices_info = ", ".join(splited)
            self.info_string += "\n{}".format(devices_info)
        if "util%" in str_data:
            splited = self.split_line(str_data)
            util_info = ", ".join(splited)
            self.info_string += "\n{}".format(util_info)
        if "thermal" in str_data:
            splited = self.split_line(str_data)
            thermal_info = ", ".join(splited)
            self.info_string += "\n{}".format(thermal_info)

            print(self.info_string)
            self.info_string = ""

    def is_running(self):
        return self.running

    def split_line(self, line):
        splited = line.split("|")
        splited = [item.strip("% \n") for item in splited]
        splited = [item for item in splited if len(item)]
        return splited


#