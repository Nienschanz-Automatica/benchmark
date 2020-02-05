import sys
from time import sleep
from subprocess import *


class HddlDaemonListener():
    def __init__(self):
        self.command = '/opt/intel/openvino/deployment_tools/inference_engine/external/hddl/bin/hddldaemon'
        self.encoding_type = "utf-8"
        self.counter = 0
        self.daemon = None
        self.running = False
        self.run_daemon()
        self.loading()

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
            splited = self.split_line(str_data)
            print("DEVICES{}\n".format(self.counter), splited, "\n")
        if "util%" in str_data:
            splited = self.split_line(str_data)
            print("UTIL{}\n".format(self.counter), splited, "\n")
        if "thermal" in str_data:
            splited = self.split_line(str_data)
            print("THERMAL{}\n".format(self.counter), splited, "\n")
            self.counter += 1
            self.running = True

    def is_running(self):
        return self.running

    def split_line(self, line):
        splited = line.split("|")
        splited = [item.strip("% \n") for item in splited]
        splited = [item for item in splited if len(item)]
        return splited


#
# if __name__ == "__main__":
#
#     def split_line(line):
#         splited = line.split("|")
#         splited = [item.strip("% \n") for item in splited]
#         splited = [item for item in splited if len(item)]
#         return splited
#
#     def get_clear_data_from_splited_line():
#         pass
#
#     command = '/opt/intel/openvino/deployment_tools/inference_engine/external/hddl/bin/hddldaemon'
#     encoding_type = "utf-8"
#     counter = 0
#
#
#     proc = Popen(command, shell=True, stdout=PIPE)
#
#     while True:
#         data = proc.stdout.readline()   # Alternatively proc.stdout.read(1024)
#         str_data = data.decode(encoding=encoding_type)
#         if "deviceId" in str_data:
#             splited = split_line(str_data)
#             print("DEVICES{}\n".format(counter), splited, "\n")
#         if "util%" in str_data:
#             splited = split_line(str_data)
#             print("UTIL{}\n".format(counter), splited, "\n")
#         if "thermal" in str_data:
#             splited = split_line(str_data)
#             print("THERMAL{}\n".format(counter), splited, "\n")
#             counter += 1
#         # if len(data) == 0:
#         #     break
#         # sys.stdout.write(data)   # sys.stdout.buffer.write(data) on Python 3.x