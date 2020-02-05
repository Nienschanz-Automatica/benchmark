from subprocess import *


def split_line(line):
    splited = line.split("|")
    splited = [item.strip("% \n") for item in splited]
    splited = [item for item in splited if len(item)]
    return splited

def get_clear_data_from_splited_line():
    pass

command = '/opt/intel/openvino/deployment_tools/inference_engine/external/hddl/bin/hddldaemon'
encoding_type = "utf-8"
counter = 0


proc = Popen(command, shell=True, stdout=PIPE)

while True:
    data = proc.stdout.readline()   # Alternatively proc.stdout.read(1024)
    str_data = data.decode(encoding=encoding_type)
    if "deviceId" in str_data:
        splited = split_line(str_data)
        print("DEVICES{}\n".format(counter), splited, "\n")
    if "util%" in str_data:
        splited = split_line(str_data)
        print("UTIL{}\n".format(counter), splited, "\n")
    if "thermal" in str_data:
        splited = split_line(str_data)
        print("THERMAL{}\n".format(counter), splited, "\n")
        counter += 1
    # if len(data) == 0:
    #     break
    # sys.stdout.write(data)   # sys.stdout.buffer.write(data) on Python 3.x