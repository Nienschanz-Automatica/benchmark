import psutil
from time import sleep, time
from datetime import datetime
import logging
import os


def get_memory_str(memory_data):
    total = memory_data.total // (1024 ** 2)
    available = memory_data.available // (1024 ** 2)
    used = memory_data.used // (1024 ** 2)
    percent = memory_data.percent
    return "RAM: [total: {}, available: {}, used: {}, percent: {}]".format(total,
                                                                           available,
                                                                           used,
                                                                           percent)


def get_cpu_usage_str(cpu_data):
    cores_names = ("cpu_{}: ".format(n) for n in range(1, len(cpu_data) + 1))
    cpu_usage_str = ""
    for core_name, usage in zip(cores_names, cpu_data):
        cpu_usage_str = cpu_usage_str + core_name + str(usage) + ", "
    cpu_usage_str = cpu_usage_str[:-2]
    return "CPU usage: [{}]".format(cpu_usage_str)


def get_temperature_str(temp_data):
    if "pch_skylake" in temp_data.keys():
        pch_skylake_temp = temp_data["pch_skylake"][0].current
    else:
        pch_skylake_temp = ""
    cores_data = temp_data["coretemp"][1:]

    temperature_string = "pch_skylake: {}, ".format(pch_skylake_temp)

    for data in cores_data:
        label = "_".join(data.label.split(" "))
        temp = data.current
        temperature_string += "{}: {}, ".format(label, temp)

    temperature_string = "Temp: " + temperature_string[:-2]
    return temperature_string


def get_data_time():
    return datetime.now().strftime("%d-%m-%Y %H:%M:%S")


def get_system_info():
    cores_usage = psutil.cpu_percent(percpu=True)
    temperatures = psutil.sensors_temperatures()
    memory = psutil.virtual_memory()

    data_time = get_data_time()
    cores_info = get_cpu_usage_str(cores_usage)
    temp_info = get_temperature_str(temperatures)
    memory_info = get_memory_str(memory)

    return data_time + "\n" + cores_info + "\n" + temp_info + "\n" + memory_info


def init_logger():
    log_dir = os.path.join(os.getcwd(), "logs")
    data_time = ".".join(get_data_time().split(" "))
    file_name = "cpu.log.{}".format(data_time)
    path_to_save = os.path.join(log_dir, file_name)
    logging.basicConfig(filename=path_to_save, level=logging.INFO)


def logging_info(info):
    logging.info(info)


if __name__ == "__main__":
    init_logger()
    delay = 5
    last_time = time()
    info = get_system_info() + "\n"
    print(info)
    logging_info(info)
    while True:
        now = time()
        if now - last_time >= delay:
            info = get_system_info() + "\n"
            print(info)
            logging_info(info)
            last_time = now
        sleep(0.5)
